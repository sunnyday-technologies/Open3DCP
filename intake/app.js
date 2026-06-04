// Open3DCP dataset-intake page — front-end logic.
//
// Zero backend, zero secrets: this page only collects metadata, runs honest readiness checks, and
// hands off to a prefilled GitHub Issue Form (.github/ISSUE_TEMPLATE/dataset-submission.yml). The
// submission IS a GitHub Issue; identity is the submitter's GitHub account; the dataset bytes live in
// a public archive referenced by DOI. GitHub Actions validates + curates from there.

const REPO = "sunnyday-technologies/Open3DCP";
const TEMPLATE = "dataset-submission.yml";
// GitHub Issue Forms prefill from query params keyed by each field's `id`. Dropdowns and checkboxes
// cannot be prefilled via URL, so `license`, the redistribution box, and the archive-resolves box are
// set by the submitter on GitHub. Long free-text is capped so the URL stays well under browser limits.
const PREFILL = ["dataset_title", "dataset_doi", "archive_url", "source_citation", "lab_name", "declared_orcid", "schema_version", "notes"];
const NOTES_CAP = 1200;
const ORCID_RE = /^(\d{4}-){3}\d{3}[\dX]$/; // 0000-0000-0000-000X

const $ = (id) => document.getElementById(id);
const fields = $("checklist") ? [...$("checklist").querySelectorAll("li")] : [];
const btn = $("btnContinue");
const continueHint = $("continueHint");

const val = (id) => ($(id) ? $(id).value.trim() : "");

function gates() {
  const orcid = val("declared_orcid");
  return {
    dataset: !!(val("dataset_title") && val("dataset_doi") && val("archive_url")),
    provenance: !!(val("source_citation") && val("lab_name")),
    license: !!val("license"),
    orcid: orcid === "" || ORCID_RE.test(orcid),
    declarations: !!($("chk_redist")?.checked && $("chk_archive")?.checked),
  };
}

function refresh() {
  const g = gates();
  fields.forEach((li) => {
    const ok = g[li.dataset.gate];
    li.dataset.state = ok ? "pass" : "fail";
    li.querySelector(".ico").textContent = ok ? "✓" : "×";
  });
  const ready = Object.values(g).every(Boolean);
  btn.setAttribute("aria-disabled", String(!ready));
  btn.classList.toggle("disabled", !ready);
  if (ready) {
    btn.href = buildIssueUrl();
    continueHint.textContent = "Opens the GitHub submission form with your details pre-filled.";
  } else {
    btn.removeAttribute("href");
    continueHint.textContent = "Complete the readiness checks above to continue.";
  }
}

function buildIssueUrl() {
  const u = new URL(`https://github.com/${REPO}/issues/new`);
  u.searchParams.set("template", TEMPLATE);
  u.searchParams.set("title", `[dataset] ${val("dataset_title")}`.slice(0, 120));
  for (const id of PREFILL) {
    let v = val(id);
    if (!v) continue;
    if (id === "notes") v = v.slice(0, NOTES_CAP);
    u.searchParams.set(id, v);
  }
  return u.toString();
}

function wire() {
  ["input", "change"].forEach((ev) => {
    ["dataset_title", "dataset_doi", "archive_url", "source_citation", "lab_name", "declared_orcid", "license", "schema_version", "chk_redist", "chk_archive"].forEach((id) => {
      const node = $(id);
      if (node) node.addEventListener(ev, refresh);
    });
  });
  btn.addEventListener("click", (e) => {
    if (btn.getAttribute("aria-disabled") === "true" || !btn.href) { e.preventDefault(); return; }
    // let the default navigation open the prefilled issue (same tab)
  });
}

wire();
refresh();
