"""Opt-in, local-only hybrid document retrieval with lexical fallback.

This module is deliberately business-agnostic and tenant-scoped: it receives
a single Workspace object, never an unrestricted global index.

Default production behavior remains lexical BM25. Set the explicit
ICONIC_HYBRID_RETRIEVAL=1 only in isolated evaluation after independent QA.

Document embeddings are built in memory from the selected workspace and
cached by its content signature. There is no data persistence or remote call.
"""
from __future__ import annotations

from collections import defaultdict
import json
import math
import threading
from urllib.parse import urlsplit
from urllib.request import Request,urlopen


class LocalEmbeddings:
    def __init__(self, endpoint="http://127.0.0.1:8081/v1/embeddings",
                 model="/home/patrick/models/nomic-embed-text-v1.5.Q8_0.gguf",
                 timeout=10):
        parts=urlsplit(endpoint)
        if parts.scheme!="http" or parts.hostname not in ("127.0.0.1","localhost","::1"):
            raise ValueError("Embedding endpoint must remain local loopback")
        self.endpoint=endpoint
        self.model=model
        self.timeout=timeout

    def encode(self, inputs):
        if not inputs: return []
        out=[]
        for start in range(0,len(inputs),64):
            batch=inputs[start:start+64]
            req=Request(self.endpoint,data=json.dumps({
                "model":self.model,"input":batch}).encode("utf-8"),
                method="POST",headers={"Content-Type":"application/json"})
            with urlopen(req,timeout=self.timeout) as r:
                result=json.load(r)
            data=sorted(result["data"],key=lambda x:x["index"])
            vec=[d["embedding"] for d in data]
            if len(vec)!=len(batch) or any(len(v)==0 or len(v)!=len(vec[0]) for v in vec):
                raise ValueError("Invalid embedding response shape")
            out.extend(vec)
        return out


def cosine(left,right):
    if len(left)!=len(right) or not left: return 0
    dot=sum(float(x)*float(y) for x,y in zip(left,right))
    mag=math.sqrt(sum(float(x)*float(x) for x in left))
    mag2=math.sqrt(sum(float(x)*float(x) for x in right))
    return dot / max(1e-12,mag*mag2)


class HybridRetriever:
    def __init__(self, embedder=None):
        self.embedder=embedder or LocalEmbeddings()
        self.lock=threading.Lock()
        self.cache={}

    def _snapshot(self,workspace):
        with workspace.lock:
            chunks=list(workspace.chunks)
            docs={d["id"]:dict(d) for d in workspace.docs}
            signature=workspace.signature
        return chunks,docs,signature

    def _vectors(self,workspace,chunks,docs,signature):
        cache_key=(workspace.id,str(getattr(workspace,"path",workspace.id)),signature)
        with self.lock:
            entry=self.cache.get(cache_key)
            if entry is not None and len(entry)==len(chunks):
                return entry
        texts=[
            "search_document: " + docs[c["doc"]]["title"] + "\n" +
            docs[c["doc"]]["rel"] + "\n" + c["text"]
            for c in chunks
        ]
        embedded=self.embedder.encode(texts)
        if len(embedded)!=len(chunks):
            raise ValueError("Embedding count mismatch")
        with self.lock:
            # Throw away old indexes for this workspace upon reindex.
            self.cache={k:v for k,v in self.cache.items()
                        if k[:2]!=cache_key[:2]}
            self.cache[cache_key]=embedded
        return embedded

    def search(self,workspace,question,k=6,per_doc=2):
        """Return the same (rank_score, chunk) interface as Workspace.search."""
        lexical=workspace.search(question,k=1000,per_doc=1000)
        try:
            chunks,docs,signature=self._snapshot(workspace)
            if not chunks:return []
            vectors=self._vectors(workspace,chunks,docs,signature)
            query_vector=self.embedder.encode(["search_query: "+str(question)[:2500]])[0]
            sem_best={}
            for c,vec in zip(chunks,vectors):
                score=cosine(query_vector,vec)
                doc=c["doc"]
                if doc not in sem_best or score>sem_best[doc][0]:
                    sem_best[doc]=(score,c)
            sem_order=sorted(sem_best,key=lambda d:-sem_best[d][0])
            lexical_best={}
            for index,(score,c) in enumerate(lexical):
                lexical_best.setdefault(c["doc"],(index+1,c))
            # Reciprocal rank fusion, same document only once.
            ranks={doc:1/(60+i) for i,doc in enumerate(sem_order,1)}
            for doc,(rank,c) in lexical_best.items():
                ranks[doc]=ranks.get(doc,0)+1/(60+rank)
            if not ranks:return lexical[:k]
            ranked=sorted(ranks,key=lambda d:(-ranks[d],-sem_best[d][0],d))
            out=[]
            for doc in ranked:
                if doc in lexical_best:
                    selected=lexical_best[doc][1]
                else:
                    selected=sem_best[doc][1]
                out.append((ranks[doc]*100.0,selected))
                if len(out)>=k:break
            # Never use a set of document-index IDs from an obsolete index
            # after a file watcher has reindexed the selected workspace.
            with workspace.lock:
                unchanged=(workspace.signature==signature)
            return out if unchanged else workspace.search(question,k=k,per_doc=per_doc)
        except Exception:
            # Failure of the auxiliary local embedding service must never
            # take down the demo or remove keyword search.
            return workspace.search(question,k=k,per_doc=per_doc)


RETRIEVER=HybridRetriever()
