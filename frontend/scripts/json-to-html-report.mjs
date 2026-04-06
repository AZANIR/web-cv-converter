#!/usr/bin/env node
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'

const jsonPath = resolve(import.meta.dirname, '../../test-reports/frontend/results.json')
const htmlPath = resolve(import.meta.dirname, '../../test-reports/frontend/report.html')

mkdirSync(dirname(htmlPath), { recursive: true })

const raw = JSON.parse(readFileSync(jsonPath, 'utf-8'))

const totalTests = raw.numTotalTests ?? 0
const passed = raw.numPassedTests ?? 0
const failed = raw.numFailedTests ?? 0
const skipped = (raw.numPendingTests ?? 0) + (raw.numTodoTests ?? 0)
const duration = ((raw.testResults ?? []).reduce((s, f) => s + (f.endTime - f.startTime), 0) / 1000).toFixed(2)
const allPassed = failed === 0
const timestamp = new Date(raw.startTime).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function statusIcon(status) {
  if (status === 'passed') return '<span class="icon pass">&#10003;</span>'
  if (status === 'failed') return '<span class="icon fail">&#10007;</span>'
  return '<span class="icon skip">&#9711;</span>'
}

let suiteRows = ''
for (const file of raw.testResults ?? []) {
  const fname = file.name.replace(/\\/g, '/').split('/frontend/')[1] ?? file.name
  const fileDur = ((file.endTime - file.startTime) / 1000).toFixed(2)
  const fileStatus = file.status === 'passed' ? 'pass' : 'fail'

  suiteRows += `<details class="suite ${fileStatus}" ${fileStatus === 'fail' ? 'open' : ''}>`
  suiteRows += `<summary><span class="suite-name">${escapeHtml(fname)}</span><span class="suite-meta">${fileDur}s</span></summary>`
  suiteRows += '<table class="tests">'

  for (const tc of file.assertionResults ?? []) {
    const ms = tc.duration != null ? `${tc.duration}ms` : ''
    const title = tc.ancestorTitles?.length ? tc.ancestorTitles.join(' > ') + ' > ' + tc.title : tc.title
    suiteRows += `<tr class="${tc.status}">`
    suiteRows += `<td class="td-icon">${statusIcon(tc.status)}</td>`
    suiteRows += `<td class="td-name">${escapeHtml(title)}</td>`
    suiteRows += `<td class="td-dur">${ms}</td>`
    suiteRows += '</tr>'
    if (tc.status === 'failed' && tc.failureMessages?.length) {
      suiteRows += `<tr><td colspan="3"><pre class="err">${escapeHtml(tc.failureMessages.join('\n'))}</pre></td></tr>`
    }
  }

  suiteRows += '</table></details>'
}

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Frontend Test Report</title>
<style>
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body{font-family:Inter,system-ui,-apple-system,sans-serif;background:#f8f9fb;color:#1e293b}
  .hdr{background:#0f172a;color:#fff;padding:1.5rem;text-align:center}
  .hdr h1{font-size:1.25rem;font-weight:700}
  .hdr .sub{color:#94a3b8;font-size:.8rem;margin-top:.25rem}
  .summary{display:flex;justify-content:center;gap:1.5rem;padding:1.25rem;flex-wrap:wrap}
  .stat{text-align:center;min-width:80px}
  .stat .num{font-size:1.75rem;font-weight:700;line-height:1}
  .stat .lbl{font-size:.7rem;color:#64748b;text-transform:uppercase;letter-spacing:.04em;margin-top:.2rem}
  .stat.pass .num{color:#16a34a} .stat.fail .num{color:#dc2626} .stat.skip .num{color:#94a3b8} .stat.time .num{color:#2563eb}
  .bar{height:6px;display:flex;max-width:600px;margin:0 auto 1.5rem;border-radius:3px;overflow:hidden}
  .bar .g{background:#22c55e} .bar .r{background:#ef4444} .bar .y{background:#e2e8f0}
  .content{max-width:820px;margin:0 auto;padding:0 1rem 2rem}
  details.suite{background:#fff;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:.75rem;overflow:hidden}
  details.suite.fail{border-color:#fecaca}
  summary{padding:.75rem 1rem;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-size:.85rem;font-weight:600;user-select:none}
  summary:hover{background:#f1f5f9}
  .suite-meta{font-weight:400;color:#94a3b8;font-size:.75rem}
  table.tests{width:100%;border-collapse:collapse}
  table.tests tr{border-top:1px solid #f1f5f9}
  table.tests td{padding:.4rem .75rem;font-size:.8rem;vertical-align:top}
  .td-icon{width:24px;text-align:center}
  .td-dur{width:60px;text-align:right;color:#94a3b8;font-size:.75rem}
  .icon{font-weight:700;font-size:.85rem}
  .icon.pass{color:#16a34a} .icon.fail{color:#dc2626} .icon.skip{color:#94a3b8}
  tr.failed .td-name{color:#dc2626}
  pre.err{background:#fef2f2;color:#991b1b;padding:.5rem;border-radius:4px;font-size:.7rem;overflow-x:auto;max-height:200px;margin:.25rem 0}
  .footer{text-align:center;padding:1rem;font-size:.7rem;color:#94a3b8}
  .badge-ok{background:#dcfce7;color:#16a34a;padding:.15rem .5rem;border-radius:4px;font-size:.7rem;font-weight:600;margin-left:.5rem}
  .badge-fail{background:#fee2e2;color:#dc2626;padding:.15rem .5rem;border-radius:4px;font-size:.7rem;font-weight:600;margin-left:.5rem}
</style>
</head>
<body>
<div class="hdr">
  <h1>Frontend Test Report <span class="${allPassed ? 'badge-ok' : 'badge-fail'}">${allPassed ? 'ALL PASSED' : failed + ' FAILED'}</span></h1>
  <div class="sub">${timestamp} &middot; ${totalTests} tests in ${(raw.testResults ?? []).length} files &middot; ${duration}s</div>
</div>
<div class="summary">
  <div class="stat pass"><div class="num">${passed}</div><div class="lbl">Passed</div></div>
  <div class="stat fail"><div class="num">${failed}</div><div class="lbl">Failed</div></div>
  <div class="stat skip"><div class="num">${skipped}</div><div class="lbl">Skipped</div></div>
  <div class="stat time"><div class="num">${duration}s</div><div class="lbl">Duration</div></div>
</div>
<div class="bar"><div class="g" style="flex:${passed}"></div><div class="r" style="flex:${failed}"></div><div class="y" style="flex:${skipped || 0.001}"></div></div>
<div class="content">${suiteRows}</div>
<div class="footer">Generated by vitest json-to-html-report</div>
</body>
</html>`

writeFileSync(htmlPath, html)
console.log(`Report written to ${htmlPath}`)
