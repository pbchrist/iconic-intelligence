"""Hybrid retrieval contracts: tenant isolation, fallback and cache invalidation."""
from collections import Counter
import threading
import unittest

import retrieval_pipeline
import server


class FakeWorkspace:
    def __init__(self,name,word):
        self.id=name
        self.signature="v1-"+name
        self.lock=threading.Lock()
        self.docs=[{"id":0,"title":name+" account report",
                    "rel":"private/account.md","text":word}]
        self.chunks=[{"doc":0,"i":0,"text":word,"tf":Counter(word.lower().split()),"len":3}]
        self.query_log=[]

    def search(self,question,k=6,per_doc=2):
        self.query_log.append(question)
        if not self.chunks:
            return []
        if any(v in question.casefold() for v in self.chunks[0]["text"].casefold().split()):
            return [(7.5,self.chunks[0])]
        return []


class FixedEmbedding:
    def __init__(self):
        self.calls=0
        self.input_log=[]
        self.fail=False

    def encode(self,inputs):
        self.calls+=1
        self.input_log.extend(inputs)
        if self.fail:raise OSError("local embedding unavailable")
        out=[]
        for prompt in inputs:
            word=prompt.lower()
            if "orchid" in word:out.append([1.0,0.0,0.0])
            elif "brass" in word:out.append([0.0,1.0,0.0])
            else:out.append([0.0,0.0,1.0])
        return out


class HybridContracts(unittest.TestCase):
    def test_public_network_embedding_endpoint_rejected(self):
        for addr in ("https://localhost/v1/embeddings",
                     "http://1.2.3.4/v1/embeddings",
                     "http://internal.example.net/v1/embeddings"):
            with self.subTest(addr=addr), self.assertRaises(ValueError):
                retrieval_pipeline.LocalEmbeddings(endpoint=addr)

    def test_no_cross_tenant_document_or_embedding(self):
        embed=FixedEmbedding()
        retriever=retrieval_pipeline.HybridRetriever(embed)
        orchid=FakeWorkspace("tenant-one","orchid")
        brass=FakeWorkspace("tenant-two","brass")
        a=retriever.search(orchid,"orchid",k=6)
        self.assertEqual([x[1]["doc"] for x in a],[0])
        self.assertNotIn("brass",str(embed.input_log).lower())
        retriever.search(brass,"brass",k=6)
        self.assertEqual(len(retriever.cache),2)
        self.assertEqual({k[0] for k in retriever.cache}, {"tenant-one","tenant-two"})

    def test_local_service_failure_preserves_keyword_search(self):
        embed=FixedEmbedding()
        embed.fail=True
        retriever=retrieval_pipeline.HybridRetriever(embed)
        w=FakeWorkspace("tenant-one","orchid")
        hits=retriever.search(w,"orchid")
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0][0],7.5)

    def test_cache_reused_and_invalidated_when_doc_changes(self):
        embed=FixedEmbedding()
        retriever=retrieval_pipeline.HybridRetriever(embed)
        w=FakeWorkspace("tenant-one","orchid")
        retriever.search(w,"orchid")
        self.assertEqual(embed.calls,2)
        retriever.search(w,"orchid")
        self.assertEqual(embed.calls,3)
        w.signature="v2-tenant-one"
        w.chunks[0]["text"]="orchid revised policy"
        retriever.search(w,"orchid")
        self.assertEqual(embed.calls,5)
        self.assertEqual(len(retriever.cache),1)

    def test_no_documents_fails_safe(self):
        embed=FixedEmbedding()
        retriever=retrieval_pipeline.HybridRetriever(embed)
        w=FakeWorkspace("tenant-one","orchid")
        w.chunks=[]
        self.assertEqual(retriever.search(w,"anything"),[])

    def test_live_default_hybrid_is_off(self):
        self.assertFalse(server.HYBRID_RETRIEVAL_ENABLED)


if __name__=="__main__":
    unittest.main()
