# TEKNOFEST Adres Çözümleme Projesi - Claude Project Knowledge Base

**Project Name:** TEKNOFEST 2025 Yapay Zeka Destekli Adres Çözümleme Yarışması  
**Target Date:** 21 Gün (1-21 Ağustos 2025)  
**Current Status:** Ready to Start - Task 1.1.1  
**Total Tasks:** 39 tasks across 6 phases

---

## 🎯 PROJECT OVERVIEW

### Mission Statement
Türkçe adreslerdeki yazım farklılıklarını, kısaltmaları ve hataları düzelterek, aynı adresleri yüksek doğrulukla eşleştiren, açıklanabilir ve production-ready yapay zeka sistemi geliştirmek.

### Success Targets
- **Kaggle F1-Score:** > 0.85
- **Processing Speed:** < 100ms per address  
- **API Response Time:** < 200ms
- **System Accuracy:** > 87% on test dataset
- **Final Ranking:** TEKNOFEST Top 3

---

## 📁 PROJECT STRUCTURE

### Core Documents (Already Available)
1. **`teknofest_prd.md`** - Complete technical specifications (Algorithm details, Database schema, API specs, Demo requirements)
2. **`teknofest_project_plan.md`** - 39 trackable tasks across 6 phases with validation criteria
3. **`claude_code_workflow.md`** - Optimization guidelines for Claude Code sessions
4. **`post_kaggle_strategy.md`** - Final hackathon preparation strategy

### Project File Organization
```
/TEKNOFEST_PROJECT/
├── docs/
│   ├── teknofest_prd.md           # Technical specifications
│   ├── teknofest_project_plan.md  # Task roadmap
│   ├── claude_code_workflow.md    # Development workflow
│   └── post_kaggle_strategy.md    # Final strategy
├── src/                           # [TO BE CREATED]
├── tests/                         # [TO BE CREATED]
├── database/                      # [TO BE CREATED]  
├── notebooks/                     # [TO BE CREATED]
└── README.md                      # [TO BE CREATED]
```

---

## 🚀 CURRENT STATUS & NEXT STEPS

### Immediate Next Task: 1.1.1
**Task:** Create directory structure  
**Instruction:** "PRD.md'deki klasör yapısını oluştur: src/, tests/, database/, notebooks/"  
**Expected Output:** Complete folder structure  
**Validation:** All directories exist, matches PRD structure  
**Status:** ⏳ Ready to Execute

### Progress Tracking
```
Overall Progress: [ 0/39 ] Tasks Completed (0%)

Phase 1: [ 0/11 ] Foundation Setup (0%)
Phase 2: [ 0/13 ] Core Algorithms (0%)  
Phase 3: [ 0/6  ] Database Integration (0%)
Phase 4: [ 0/4  ] API Development (0%)
Phase 5: [ 0/2  ] Demo Application (0%)
Phase 6: [ 0/4  ] Performance & Deployment (0%)
```

---

## 🎯 CLAUDE CODE WORKING INSTRUCTIONS

### Task Execution Template
When executing any task, always use this format:

```
=== CLAUDE CODE TASK EXECUTION ===

**TASK IDENTIFICATION:**
- Task ID: [from project plan]
- Phase: [current phase]
- Priority: [Critical/High/Medium]

**PRD REFERENCE:**
- Section: [exact PRD.md section]
- Specification: [key requirements]

**TASK INSTRUCTION:**
[exact instruction from project plan]

**DELIVERABLE SPECIFICATION:**
- Primary Output: [main deliverable]
- Quality Standards: [requirements]

**VALIDATION CRITERIA:**
[how to verify success]

**CONTEXT & DEPENDENCIES:**
- Completed Prerequisites: [previous tasks]
- Required Components: [dependencies]

**AUTO-PROGRESS INSTRUCTION:**
After completing this task, automatically:
1. Update project plan checkbox for Task [ID] to ✅
2. Update phase progress counter
3. Update overall progress counter
4. Set completion timestamp
5. Add completion notes
```

### Key Principles
1. **One Task at a Time:** Complete each task fully before moving to next
2. **Validation Required:** Each task must pass validation criteria
3. **Progress Tracking:** Update project plan after each completed task
4. **PRD Compliance:** Always reference PRD.md for technical specifications
5. **Quality First:** Meet all quality standards before marking complete

---

## 🏗️ TECHNICAL ARCHITECTURE OVERVIEW

### 4 Core Algorithms (From PRD)
1. **AddressValidator** (`src/address_validator.py`) - Hiyerarşik tutarlılık kontrolü
2. **AddressCorrector** (`src/address_corrector.py`) - Yazım hataları düzeltme  
3. **AddressParser** (`src/address_parser.py`) - Bileşen ayrıştırma
4. **HybridAddressMatcher** (`src/address_matcher.py`) - Multi-level benzerlik

### System Components
- **Database:** PostgreSQL + PostGIS (spatial queries)
- **API:** FastAPI (async endpoints)
- **Demo:** Streamlit (6-tab interface with transformation story)
- **Pipeline:** GeoIntegratedPipeline (end-to-end processing)

### Technology Stack
```python
# Key Dependencies
pandas>=1.5.0, scikit-learn>=1.3.0, sentence-transformers>=2.2.0
transformers>=4.30.0, torch>=2.0.0, fastapi>=0.100.0
streamlit>=1.25.0, psycopg2-binary>=2.9.0, geopy>=2.3.0
thefuzz>=0.19.0, pytest>=7.4.0
```

---

## 📋 PHASE BREAKDOWN

### Phase 1: Foundation Setup (Days 1-3) - 11 Tasks
**Objective:** Setup project infrastructure and external data
- **Tasks 1.1.x:** Project structure, requirements, Git setup
- **Tasks 1.2.x:** Database schema creation  
- **Tasks 1.3.x:** Pydantic models
- **Tasks 1.4.x:** External data sourcing (NEW - hierarchy, abbreviations, spelling)

### Phase 2: Core Algorithms (Days 4-10) - 13 Tasks  
**Objective:** Implement and test all 4 algorithms
- **Test-First Approach:** Write tests before implementation
- **Turkish-Specific:** Focus on Turkish language features
- **Performance:** Meet accuracy targets (>80-90% per algorithm)
- **Robustness:** Handle edge cases gracefully (NEW)

### Phase 3: Database Integration (Days 11-13) - 6 Tasks
**Objective:** PostgreSQL + PostGIS integration
- **Spatial Queries:** Geographic matching capabilities
- **Pipeline Integration:** End-to-end processing
- **Performance:** <100ms per address target

### Phase 4: API Development (Days 14-15) - 4 Tasks
**Objective:** FastAPI endpoints and documentation
- **5 Main Endpoints:** /process, /batch, /match, /health, /metrics
- **Response Time:** <200ms target
- **Documentation:** Complete OpenAPI specs

### Phase 5: Demo Application (Days 16-17) - 2 Tasks
**Objective:** Streamlit demo for TEKNOFEST presentation
- **6-Tab Interface:** Including new "Adres Dönüşüm Hikayesi"
- **Interactive:** Real-time processing visualization
- **Explainable:** Step-by-step transformation story

### Phase 6: Performance & Deployment (Days 18-21) - 4 Tasks
**Objective:** Optimization and production readiness
- **Performance Testing:** Automated test suite
- **Docker Deployment:** Full-stack containerization
- **TEKNOFEST Ready:** Complete demo preparation

---

## 🎯 CRITICAL SUCCESS FACTORS

### Technical Requirements
- **F1-Score:** Must exceed 0.80 (target: 0.85+)
- **Speed:** Processing time <100ms per address
- **Reliability:** System uptime >99% during demo
- **Scalability:** Handle 1000+ concurrent requests

### TEKNOFEST Specific
- **Turkish Language:** Deep understanding of Turkish address patterns
- **Explainability:** Clear decision reasoning for jüri
- **Demo Quality:** Flawless live demonstration
- **Innovation:** Unique hybrid approach (semantic + geographic + textual + hierarchical)

### Quality Gates
- **Phase Completion:** All tasks must pass validation before next phase
- **Integration Testing:** Components must work together
- **Performance Benchmarks:** Must meet speed/accuracy targets
- **Demo Rehearsal:** Multiple successful demo runs required

---

## 🚨 RISK MANAGEMENT

### High-Risk Areas
1. **Turkish NLP Complexity:** Language-specific challenges
2. **Database Integration:** PostGIS spatial queries complexity  
3. **Real-time Performance:** Meeting speed requirements
4. **Demo Stability:** Live presentation risks

### Mitigation Strategies
- **Incremental Development:** Test after each task
- **Backup Plans:** Offline demo capabilities
- **Performance Monitoring:** Continuous benchmarking
- **Quality Assurance:** Comprehensive test coverage

---

## 📞 SUPPORT & GUIDANCE

### When You Need Help
1. **Technical Questions:** Reference PRD.md for specifications
2. **Task Clarification:** Check project plan validation criteria  
3. **Workflow Issues:** Follow claude_code_workflow.md guidelines
4. **Performance Problems:** Review optimization techniques in workflow

### Decision Framework
- **Priority:** Critical path tasks first (database schema → algorithms → integration)
- **Quality:** Never compromise on validation criteria
- **Speed:** Optimize for rapid iteration within quality bounds
- **Integration:** Consider impact on downstream tasks

---

## 🎉 READY TO START!

**Current Task:** 1.1.1 - Create directory structure  
**Next 3 Tasks:** 1.1.2 (requirements.txt), 1.1.3 (Git setup), 1.2.1 (database schema)

**Success Indicators:**
- ✅ Each task passes validation criteria
- ✅ Progress counters update correctly  
- ✅ System maintains quality standards
- ✅ Timeline stays on track

**Remember:** This is a winning TEKNOFEST project. Every task contributes to our final success. Quality, consistency, and Turkish-language expertise are our competitive advantages.

**LET'S BUILD SOMETHING AMAZING! 🚀**