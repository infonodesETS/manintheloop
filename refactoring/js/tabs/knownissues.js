'use strict';

export default async function initKnownIssues() {
  const body = document.getElementById('knownissues-body');
  try {
    const res  = await fetch('known-issues.md');
    const text = await res.text();
    body.innerHTML = window.marked.parse(text);
  } catch (err) {
    body.innerHTML = `<p style="color:#ff4444">Failed to load known-issues.md</p>`;
  }
}
