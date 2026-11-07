"""Exact Case 43 browser regrade with live model, real workspace GETs and no mocks."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

BASE=os.environ.get('ICONIC_DEMO_TEST_BASE','http://127.0.0.1:8797')
OUT=Path(os.environ.get('ICONIC_CASE43_OUT','/tmp/iconic-demo45-case43-browser.json'))
result=[]
def switch(p,w):
    p.locator('#wsChip').click()
    expect(p.locator('#wsMenu button[data-ws="'+w+'"]')).to_be_visible(timeout=10000)
    p.locator('#wsMenu button[data-ws="'+w+'"]').click()
    expect(p.locator('#wsName')).to_contain_text('Northline' if w=='northline-supply' else 'Hollis',timeout=12000)
def ask(p,q):
    old=p.locator('#convo .turn').count()
    p.locator('#askInput').fill(q)
    p.locator('#askBtn').click()
    expect(p.locator('#convo .turn')).to_have_count(old+1,timeout=20000)
    expect(p.locator('#askBtn')).to_be_enabled(timeout=30000)
    ans=p.locator('#convo .turn .a-body').last.inner_text()
    src=p.locator('#convo .turn').last.locator('.src strong').all_inner_texts()
    print('TURN',q,'=>',ans[:270].replace('\n',' / '),flush=True)
    return {'q':q,'answer':ans,'sources':src}
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/home/patrick/.local/bin/google-chrome',args=['--no-sandbox'])
    for w,h in [(1280,850),(390,844)]:
        page=b.new_page(viewport={'width':w,'height':h})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE+'/?embed=1',wait_until='domcontentloaded',timeout=20000)
        switch(page,'northline-supply')
        a=ask(page,'Who is our office manager?')
        assert 'Gina Moss' in a['answer']
        page.reload(wait_until='domcontentloaded')
        expect(page.locator('#convo .turn')).to_have_count(1,timeout=15000)
        x=ask(page,'Who is our office manager?')
        assert 'Gina Moss' in x['answer']
        page.reload(wait_until='domcontentloaded')
        expect(page.locator('#convo .turn')).to_have_count(2,timeout=15000)
        y=ask(page,'And who prepared our slow-moving inventory report?')
        assert 'Gina Moss' in y['answer']
        switch(page,'hollis-reyes')
        expect(page.locator('#convo .turn')).to_have_count(0,timeout=10000)
        page.reload(wait_until='domcontentloaded')
        expect(page.locator('#wsName')).to_contain_text('Hollis',timeout=15000)
        expect(page.locator('#convo .turn')).to_have_count(0,timeout=15000)
        z=ask(page,'Who prepared our Q3 billing report, and what did you tell me about Gina a minute ago?')
        assert 'Sam Ortiz' in z['answer']
        assert '$1,284,000' not in z['answer']
        assert 'Gina Moss' not in z['answer']
        assert any('Q3 2026 billing report' in t for t in z['sources'])
        assert not errors,errors
        result.append({'viewport_width':w,'pass':True,'northline_first':a,'northline_repeat':x,
                       'northline_report_preparer':y,'hollis_after_switch':z})
        print('CASE43_REAL_BROWSER_PASS',w,flush=True)
        page.close()
    b.close()
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps({'schema':'case43-real-browser-v1','base':BASE,'results':result},indent=2))
OUT.chmod(0o600)
print('SAVED',OUT,flush=True)
