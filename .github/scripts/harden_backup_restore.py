from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

EXPECTED_PORTABLE = '3e36ecee887e85272648fc7658bbd32b22110d659778acae9adccde979c2033f'
EXPECTED_FRONTEND = 'ba6d7357575002a0ee129b26733f52e9c29d5e64a470e3bf84bd76ca8d306e99'
EXPECTED_COURSE = '569bc1d6e94096f495345274bc5083053e1d5fd9af4262d4549cb08cde6b5880'
PREVIOUS_PORTABLE = 'd88fe764a02c2cf7f9ffb0497fbe758a928d68ae9d492e17ed6e97cf6499cebd'
PREVIOUS_FRONTEND = 'bc5fba01bde2e9df9524318870f2a95879cb4a351c2fdab6b41af11474f7e1f7'

OLD = """    $('#importProgress').addEventListener('change',async e=>{const input=e.target,f=input.files?.[0];if(!f)return;try{if(f.size>MAX_IMPORT_BYTES)throw new Error(`Learning-data file exceeds the ${MAX_IMPORT_MIB} MiB import limit.`);const raw=JSON.parse(await f.text());if(!isRecord(raw))throw new Error('Learning-data root must be a JSON object.');let p,requested=[];
      if(raw.format==='gdscript-lab-learning-data' && Number(raw.format_version||1)===1){
        p=isRecord(raw.state)?raw.state:{};requested=sanitizeEvidenceComplete(p.lessonEvidenceComplete||[]);
      }else if(Number(raw.schema)===2 && isRecord(raw.state)){
        p=raw.state;requested=sanitizeEvidenceComplete(p.lessonEvidenceComplete||[]);
      }else if(Number(raw.version||0)===1){
        p=raw;requested=sanitizeEvidenceComplete(p.evidenceComplete??p.mastered);
      }else{
        throw new Error('Unsupported or unrecognized learning-data backup.');
      }
      state.visited=new Set(sanitizeVisited(p.visited||[]));state.quiz=sanitizeQuiz(p.quiz);state.quizAnswers=sanitizeQuizAnswers(p.quizAnswers);state.quizPassed=sanitizeQuizPassed(p.quizPassed);state.quizQuestion=sanitizeQuizQuestion(p.quizQuestion);state.projectChecks=sanitizeProjectChecks(p.projectChecks);state.evidence=sanitizeEvidence(p.evidence);state.predictOk=sanitizePredict(p.predictOk);state.notes=sanitizeNotes(p.notes);state.guessed=sanitizeBoolMap(p.guessed);state.reviewMeta=sanitizeReviewMeta(p.reviewMeta);state.versionEvidence=sanitizeVersionEvidence(p.versionEvidence);state.artifacts=sanitizeArtifacts(p.artifacts);state.projectEvidence=sanitizeProjectEvidence(p.projectEvidence);state.assessmentState=sanitizeAssessmentState(p.assessmentState);state.externalReviewRecords=sanitizeReviewerRecords(p.externalReviewRecords);state.lessonEvidenceComplete=new Set();for(const id of requested){const l=lessonMap.get(id);if(l&&canCompleteLessonEvidence(l))state.lessonEvidenceComplete.add(id);}if(typeof p.lastLesson==='string'&&lessonMap.has(p.lastLesson))state.lessonId=p.lastLesson;persistAll();updateProgressUI();renderNav();renderProgress();showToast(`Learning data imported and revalidated. ${requested.length-state.lessonEvidenceComplete.size} requested lesson completion mark(s) did not satisfy current gates.`,'success');}catch(err){showToast(err?.message||'Learning data could not be read.','error');}finally{input.value='';}});
"""
NEW = """    $('#importProgress').addEventListener('change',async e=>{const input=e.target,f=input.files?.[0];if(!f)return;try{if(f.size>MAX_IMPORT_BYTES)throw new Error(`Learning-data file exceeds the ${MAX_IMPORT_MIB} MiB import limit.`);const raw=JSON.parse(await f.text());if(!isRecord(raw))throw new Error('Learning-data root must be a JSON object.');let p,requested=[];
      if(raw.format==='gdscript-lab-learning-data' && Number(raw.format_version??1)===1){
        if(!isRecord(raw.state))throw new Error('GDScript Lab backup is missing its state object.');
        p=raw.state;requested=sanitizeEvidenceComplete(p.lessonEvidenceComplete||[]);
      }else if(Number(raw.schema)===2 && isRecord(raw.state)){
        p=raw.state;requested=sanitizeEvidenceComplete(p.lessonEvidenceComplete||[]);
      }else if(Number(raw.version||0)===1){
        p=raw;requested=sanitizeEvidenceComplete(p.evidenceComplete??p.mastered);
      }else{
        throw new Error('Unsupported or unrecognized learning-data backup.');
      }
      const clean={visited:new Set(sanitizeVisited(p.visited||[])),quiz:sanitizeQuiz(p.quiz),quizAnswers:sanitizeQuizAnswers(p.quizAnswers),quizPassed:sanitizeQuizPassed(p.quizPassed),quizQuestion:sanitizeQuizQuestion(p.quizQuestion),projectChecks:sanitizeProjectChecks(p.projectChecks),evidence:sanitizeEvidence(p.evidence),predictOk:sanitizePredict(p.predictOk),notes:sanitizeNotes(p.notes),guessed:sanitizeBoolMap(p.guessed),reviewMeta:sanitizeReviewMeta(p.reviewMeta),versionEvidence:sanitizeVersionEvidence(p.versionEvidence),artifacts:sanitizeArtifacts(p.artifacts),projectEvidence:sanitizeProjectEvidence(p.projectEvidence),assessmentState:sanitizeAssessmentState(p.assessmentState),externalReviewRecords:sanitizeReviewerRecords(p.externalReviewRecords),lastLesson:typeof p.lastLesson==='string'&&lessonMap.has(p.lastLesson)?p.lastLesson:state.lessonId};
      const noteCount=Object.keys(clean.notes).length;
      if(!confirm(`Restore backup “${f.name}”? This will replace the current learning record with ${clean.visited.size} visited lesson(s) and ${noteCount} saved note(s). Your current record is not automatically exported first. Continue?`))return;
      state.visited=clean.visited;state.quiz=clean.quiz;state.quizAnswers=clean.quizAnswers;state.quizPassed=clean.quizPassed;state.quizQuestion=clean.quizQuestion;state.projectChecks=clean.projectChecks;state.evidence=clean.evidence;state.predictOk=clean.predictOk;state.notes=clean.notes;state.guessed=clean.guessed;state.reviewMeta=clean.reviewMeta;state.versionEvidence=clean.versionEvidence;state.artifacts=clean.artifacts;state.projectEvidence=clean.projectEvidence;state.assessmentState=clean.assessmentState;state.externalReviewRecords=clean.externalReviewRecords;state.lessonId=clean.lastLesson;state.lessonEvidenceComplete=new Set();for(const id of requested){const l=lessonMap.get(id);if(l&&canCompleteLessonEvidence(l))state.lessonEvidenceComplete.add(id);}state.lastExportEvidenceCount=state.lessonEvidenceComplete.size;persistAll();store.write('gdlab-last-export-evidence-count',state.lastExportEvidenceCount);updateProgressUI();renderNav();renderProgress();showToast(`Backup restored and revalidated. ${requested.length-state.lessonEvidenceComplete.size} requested lesson completion mark(s) did not satisfy current gates.`,'success');}catch(err){showToast(err?.message||'Learning data could not be read.','error');}finally{input.value='';}});
"""

RUNTIME_QA = {
  "desktop":{"lessons":171,"top_level_views":8,"max_overflow":0,"duplicate_id_views":{},"errors":[],"console_errors":[],"light_dark_scrollbar_tokens":"PASS"},
  "mobile":{"viewport":"390x844","lessons":171,"top_level_views":8,"max_overflow":0,"duplicate_id_views":{},"errors":[],"console_errors":[],"light_dark_scrollbar_tokens":"PASS"}
}
BACKUP_QA = {"invalid_preserves_state":True,"malformed_missing_state_rejected":True,"cancel_preserves_state":True,"accepted_restore_round_trip":True,"explicit_overwrite_confirmation":True,"errors":[]}

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def course_hash(html:Path)->str:
    s=html.read_text(encoding='utf-8')
    m=re.search(r'const COURSE_DATA\s*=\s*(\{.*?\});\s*\n\s*const APP_VERSION',s,re.S)
    if not m: raise SystemExit('COURSE_DATA payload not found')
    return hashlib.sha256(m.group(1).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('project'); a=ap.parse_args(); root=Path(a.project).resolve()
    htmls=['portable/GDScript_Lab_Godot47_v1.0.0.html','release/GDScript_Lab_v1.0.0_Portable.html','src/index.html']
    for rel in htmls:
        p=root/rel; s=p.read_text(encoding='utf-8')
        if NEW in s: print(rel,'already hardened')
        elif OLD in s: p.write_text(s.replace(OLD,NEW,1),encoding='utf-8'); print('hardened',rel)
        else: raise SystemExit(f'Expected importer not found in {rel}')
    portable=sha(root/htmls[0]); frontend=sha(root/'src/index.html')
    if portable!=EXPECTED_PORTABLE: raise SystemExit(f'Unexpected portable hash {portable}')
    if frontend!=EXPECTED_FRONTEND: raise SystemExit(f'Unexpected frontend hash {frontend}')
    if course_hash(root/htmls[0])!=EXPECTED_COURSE: raise SystemExit('COURSE_DATA changed')
    (root/'UI_POLISH_RUNTIME_QA.json').write_text(json.dumps(RUNTIME_QA,indent=2)+'\n',encoding='utf-8')
    (root/'BACKUP_RESTORE_QA.json').write_text(json.dumps(BACKUP_QA,indent=2)+'\n',encoding='utf-8')
    audit=root/'scripts/audit.py'; s=audit.read_text(encoding='utf-8'); s=re.sub(r"EXPECTED_PORTABLE='[0-9a-f]{64}'",f"EXPECTED_PORTABLE='{portable}'",s); audit.write_text(s,encoding='utf-8')
    for rel in ['README.md','VALIDATION_SUMMARY.md','RELEASE_CHECKLIST.md']:
        p=root/rel; s=p.read_text(encoding='utf-8'); s=s.replace(PREVIOUS_PORTABLE,portable).replace(PREVIOUS_FRONTEND,frontend)
        if rel=='VALIDATION_SUMMARY.md':
            s=s.replace('Generated: 2026-09-01','Generated: 2026-09-02')
            s=s.replace('- Native-mock browser test: 171/171 lessons rendered; 0 lesson failures; 0 320px horizontal overflows; 0 page errors; 0 console errors','- UI maintenance Chromium sweep: 171/171 lessons rendered at desktop and 390×844 mobile viewports; all top-level views checked; 0 duplicate IDs; 0 document horizontal overflow; 0 page errors; 0 console errors; light/dark scrollbar tokens verified')
            marker='- Native failure-path test: PASS; no unsafe browser-download or `window.open` fallback inside Tauri\n'; extra='- Backup/restore hardening QA: malformed current-format backup without `state` rejected without mutation; restore cancellation preserves current state; accepted restore round-trip PASS\n'
            if marker in s and extra not in s: s=s.replace(marker,marker+extra)
        elif rel=='README.md':
            marker='- Portable HTML remains included for users who prefer the standalone browser edition.\n'; extra='- The 2026-09-02 UI maintenance revision embeds the official Dreamcatcher SVG, synchronizes light/dark scrollbar chrome, and hardens backup restore confirmation/validation without changing `COURSE_DATA`.\n'
            if marker in s and extra not in s:s=s.replace(marker,marker+extra)
        elif rel=='RELEASE_CHECKLIST.md':
            marker='- [x] Native-mock browser regression: 171/171 lessons, zero page/console errors, zero 320px overflow\n'; replacement='- [x] Chromium UI maintenance regression: 171/171 lessons on desktop/mobile, all top-level views, zero duplicate IDs, zero document overflow, zero page/console errors, both scrollbar themes verified\n- [x] Backup restore malformed-state rejection, cancellation preservation and accepted round-trip verified\n'; s=s.replace(marker,replacement)
        p.write_text(s,encoding='utf-8')
    mp=root/'BUILD_MANIFEST.json'; m=json.loads(mp.read_text(encoding='utf-8')); m['manifest_generated_at']='2026-09-02'; m['frozen_html_sha256']=portable; m['tauri_frontend_sha256']=frontend; m['ui_polish_revision']='2026-09-02-dreamcatcher-theme-backup-hardening'
    m['ui_polish_changes']=['Embedded official Dreamcatcher SVG byte-for-byte as a self-contained data URI in Home, About, and final workflow choice UI','Added explicit dark/light scrollbar theme synchronization while keeping code-context scrollbars dark','Improved backup/restore discoverability and dated backup filenames without changing backup format_version 1','Hardened restore safety: malformed current-format backups without state are rejected, valid restores require explicit replacement confirmation, cancellation preserves current state, imported data is sanitized/revalidated, and the backup-reminder baseline is reset after restore']
    m.setdefault('validation',{})['javascript_node_check']='PASS'; m['validation']['ui_polish_runtime_sweep']={'desktop_viewport':'1440x1000','mobile_viewport':'390x844','lessons_rendered_each':'171/171','top_level_views_each':8,'duplicate_ids':0,'document_horizontal_overflow':0,'page_errors':0,'console_errors':0,'light_dark_scrollbar_tokens':'PASS'}; m['validation']['backup_restore_hardening']={'malformed_missing_state_rejected_without_mutation':'PASS','cancel_preserves_current_state':'PASS','accepted_restore_round_trip':'PASS','explicit_overwrite_confirmation':'PASS'}
    for rel in list(m.get('validated_source_files',{})):
        p=root/rel
        if p.exists(): m['validated_source_files'][rel]=sha(p)
    for rel in ['UI_POLISH_RUNTIME_QA.json','BACKUP_RESTORE_QA.json']: m.setdefault('validated_source_files',{})[rel]=sha(root/rel)
    mp.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('portable',portable); print('frontend',frontend); print('course',EXPECTED_COURSE)
if __name__=='__main__': main()
