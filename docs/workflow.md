# Claude Code için Optimize Edilmiş Workflow

## 🎯 WORKFLOW FELSEFESI

### Claude Code'un Güçlü Yönleri
- **Atomik Task'larda Mükemmel:** Tek, net tanımlı görevlerde çok başarılı
- **Context Takibi:** Önceki kodları hatırlayıp tutarlı geliştirme yapabiliyor  
- **Test-Driven:** Test yazıp sonra implementation yapması kolay
- **Documentation:** Otomatik docstring ve comment üretimi çok iyi
- **Refactoring:** Mevcut kodu optimize etme konusunda başarılı

### Claude Code'un Zorluk Çektiği Alanlar
- **Büyük Dosyalar:** 1000+ satır dosyalar zorluyor
- **Complex Dependencies:** Çok sayıda import ve dependency yönetimi
- **Database Integration:** Karmaşık SQL ve ORM işlemleri
- **Async Programming:** Async/await pattern'lerinde hata yapabiliyor
- **Multi-File Refactoring:** Birden fazla dosyayı aynı anda değiştirme

---

## 🛤️ OPTIMAL WORKFLOW STRATEGY

### Prensipler:
1. **Micro-Tasks:** Her task maksimum 1 dosya, 1 class, ~200 satır
2. **Test-First:** Önce test yaz, sonra implementation yap
3. **Incremental:** Küçük adımlarla ilerle, sürekli test et
4. **Single Responsibility:** Her session'da tek bir sorumluluğa odaklan
5. **Context Preservation:** Her adımda önceki kodu reference et

---

## 📋 PHASE-BY-PHASE WORKFLOW

### PHASE 1: FOUNDATION SETUP (Days 1-3)

#### Session 1.1: Project Structure
**Claude Code Task:**
```
"PRD.md'deki spesifikasyonlara göre proje klasör yapısını oluştur:
- src/ klasörü ve alt modüller
- tests/ klasörü ve test kategorileri  
- database/ klasörü ve SQL dosyaları
- requirements.txt tüm dependencies ile
- .gitignore Python projesi için
- README.md setup instructions ile"
```

**Expected Output:** Complete project skeleton
**Validation:** Folder structure matches PRD specifications

#### Session 1.2: Database Schema
**Claude Code Task:**
```
"PRD.md'deki Database Specifications bölümündeki:
- 001_create_tables.sql dosyasını oluştur
- 002_spatial_functions.sql dosyasını oluştur  
- PostGIS extension ve indexes dahil
- SQL syntax PostgreSQL 15+ uyumlu olsun"
```

**Expected Output:** Complete database schema files
**Validation:** SQL files run without errors on PostgreSQL+PostGIS

#### Session 1.4: External Data Preparation
**Claude Code Task:**
```
"External data sources için:
- database/turkey_admin_hierarchy.csv dosyasını TÜİK verilerine göre oluştur
- src/data/abbreviations.json Türkçe kısaltmalar sözlüğünü oluştur  
- src/data/spelling_corrections.json yazım hataları düzeltme sözlüğünü oluştur
- Her dosyanın validation criteria'sını karşıladığından emin ol"
```

**Expected Output:** All external data files ready
**Validation:** Data files meet minimum content requirements

### PHASE 2: CORE ALGORITHMS (Days 4-10)

#### Session 2.1: Address Validator (Test-First)
**Step 1 - Tests:**
```
"tests/test_address_validator.py dosyasını oluştur:
- PRD'deki AddressValidator class için unit tests
- validate_hierarchy, validate_postal_code, validate_coordinates methods için test cases
- Ground truth test data ile
- Pytest fixtures kullan"
```

**Step 2 - Implementation:**
```
"src/address_validator.py dosyasını oluştur:
- PRD'deki AddressValidator class specification'ını implement et
- Tüm method signatures PRD ile uyumlu olsun
- Test'leri geçecek şekilde implement et
- Type hints ve docstrings ekle"
```

**Validation:** All tests pass, coverage >90%

#### Session 2.2: Address Corrector (Test-First)
**Step 1 - Tests:**
```
"tests/test_address_corrector.py dosyasını oluştur:
- AddressCorrector class için comprehensive test suite
- Türkçe karakter düzeltme test cases
- Kısaltma expansion test cases  
- Spelling correction test cases"
```

**Step 2 - Implementation:**
```
"src/address_corrector.py dosyasını oluştur:
- PRD specification'ına göre AddressCorrector class
- Türkçe abbreviation dictionary
- Levenshtein distance based correction
- Test'leri geçen implementation"
```

**Validation:** All tests pass, Turkish-specific corrections work

#### Session 2.3: Address Parser (Test-First)
**Step 1 - Tests:**
```
"tests/test_address_parser.py dosyasını oluştur:
- AddressParser class için test suite
- Rule-based parsing test cases
- ML-based NER test cases
- Component extraction accuracy tests"
```

**Step 2 - Implementation:**
```
"src/address_parser.py dosyasını oluştur:
- PRD'deki AddressParser class
- Turkish NER model integration
- Rule-based patterns
- Hybrid parsing approach"
```

**Validation:** Parsing accuracy >85% on test data

#### Session 2.4: Hybrid Address Matcher (Test-First)
**Step 1 - Tests:**
```
"tests/test_address_matcher.py dosyasını oluştur:
- HybridAddressMatcher class test suite
- Semantic similarity tests
- Geographic similarity tests
- Ensemble scoring tests"
```

**Step 2 - Implementation:**
```
"src/address_matcher.py dosyasını oluştur:
- HybridAddressMatcher class implementation
- Sentence transformers integration
- Multi-level similarity calculation
- Weighted ensemble scoring"
```

#### Session 2.5: Robustness Testing
**Claude Code Task:**
```
"tests/test_robustness.py dosyasını oluştur:
- Edge case scenarios (anlamsız metinler, eksik bilgiler)
- System crash prevention tests
- Error handling validation
- Graceful degradation tests
- Low confidence score scenarios"
```

**Expected Output:** Comprehensive robustness test suite
**Validation:** System handles all edge cases without crashing

### PHASE 3: DATABASE INTEGRATION (Days 11-13)

#### Session 3.1: Database Manager (Test-First)
**Step 1 - Tests:**
```
"tests/test_database_manager.py dosyasını oluştur:
- PostGISManager class için integration tests
- Mock database kullanarak unit tests
- Spatial query test cases
- Connection handling tests"
```

**Step 2 - Implementation:**
```
"src/database_manager.py dosyasını oluştur:
- PRD'deki PostGISManager class
- Async database operations
- Spatial query methods
- Connection pooling"
```

**Validation:** Database operations work with real PostGIS

#### Session 3.2: Pipeline Integration
**Step 1 - Tests:**
```
"tests/test_geo_integrated_pipeline.py dosyasını oluştur:
- GeoIntegratedPipeline class için end-to-end tests
- Mock all dependencies (database, external APIs)
- Performance benchmark tests
- Error handling tests"
```

**Step 2 - Implementation:**
```
"src/geo_integrated_pipeline.py dosyasını oluştur:
- Tüm algorithm'ları entegre eden pipeline
- Async processing
- Error handling ve logging
- Confidence calculation"
```

**Validation:** Full pipeline processes addresses correctly

### PHASE 4: API DEVELOPMENT (Days 14-15)

#### Session 4.1: FastAPI Application
**Claude Code Task:**
```
"main.py dosyasını oluştur:
- PRD'deki tüm API endpoints
- Pydantic models ile validation
- Error handling ve status codes
- OpenAPI documentation
- Health check endpoint"
```

**Validation:** All endpoints work with Swagger UI

#### Session 4.2: API Tests
**Claude Code Task:**
```
"tests/test_api.py dosyasını oluştur:
- FastAPI endpoints için integration tests
- TestClient kullanarak
- Happy path ve error cases
- Performance tests"
```

**Validation:** API tests pass, response times <200ms

### PHASE 5: DEMO APPLICATION (Days 16-17)

#### Session 5.1: Enhanced Streamlit Demo
**Claude Code Task:**
```
"demo_app.py dosyasını oluştur:
- PRD'deki 6-tab interface (5 eski + 1 yeni 'Adres Dönüşüm Hikayesi')
- address_transformation_story_demo() fonksiyonunu implement et
- Step-by-step address processing visualization
- API calls ile backend entegrasyonu
- Interactive progress tracking
- Error handling ve user feedback"
```

**Expected Output:** Enhanced demo with transformation story
**Validation:** All 6 tabs work, transformation story demonstrates full pipeline

### PHASE 6: PERFORMANCE & DEPLOYMENT (Days 18-21)

#### Session 6.1: Performance Tests
**Claude Code Task:**
```
"tests/performance/test_performance.py dosyasını oluştur:
- PRD'deki performance test suite
- F1-score, processing speed tests
- Performance report generation
- Benchmark validation"
```

**Validation:** All performance targets met

#### Session 6.2: Docker Configuration  
**Claude Code Task:**
```
"Docker deployment dosyalarını oluştur:
- Dockerfile
- docker-compose.yml
- setup.sh script
- Environment configuration"
```

**Validation:** Full stack runs with docker-compose

---

## 🔄 SESSION MANAGEMENT STRATEGY

### Her Session Öncesi:
1. **Context Setting:** "PRD.md ve önceki implementation'ları referans al"
2. **Task Definition:** Tek, net, ölçülebilir görev tanımla
3. **Expected Output:** Çıktının nasıl test edileceğini belirt

### Her Session Sonrası:
1. **Code Validation:** Kodu çalıştır ve test et
2. **Integration Check:** Diğer bileşenlerle uyumunu kontrol et
3. **Documentation Update:** README ve comments güncelle

### Session Template:
```
"Claude Code Task:
Context: PRD.md'deki [specific section] ve önceki [related files]
Goal: [Single, specific objective]
Expected Output: [Exact deliverable]
Validation Criteria: [How to test success]
Dependencies: [What needs to exist first]"
```

---

## 🎯 CRITICAL SUCCESS FACTORS

### 1. **Incremental Development**
- Her session'da working code üret
- Büyük refactoring'leri birden yapma
- Sürekli test et

### 2. **Context Management**
- Her session'da PRD.md'yi reference et
- Önceki kod'ları hatırlat
- Consistency kontrol et

### 3. **Error Prevention**
- Test-first approach kullan
- Type hints ve validation ekle
- Edge cases'i düşün

### 4. **Performance Tracking**
- Her algorithm'ı benchmark'la
- Performance regression'ları yakala
- Optimization opportunities tanımla

---

## 🚨 RISK MITIGATION

### Common Claude Code Pitfalls:
1. **Import Conflicts:** Her session'da import'ları kontrol et
2. **Async Issues:** Async kod'u dikkatli test et
3. **Database Connections:** Connection pool'ları doğru yönet
4. **Memory Leaks:** Large model'ları cache'le

### Backup Strategies:
1. **Code Backup:** Her major change'de git commit
2. **Working Versions:** Her phase'de working version tag'le
3. **Rollback Plan:** Critical bug'larda önceki version'a dön

## 🔗 PROJECT PLAN INTEGRATION

### Workflow ↔ Project Plan Synchronization

Bu workflow artık `projectplan.md` ile tam entegre çalışır:

**Her Session Öncesi:**
1. **Project Plan Check:** `projectplan.md`'den next task'ı identify et
2. **PRD Reference:** Hangi PRD section'ının gerekli olduğunu belirle
3. **Task Instruction:** Project plan'deki exact Claude Code instruction'ı kullan

**Her Session Sonrası:**
1. **Validation:** Project plan'deki validation criteria'ya göre test et
2. **Status Update:** Task checkbox'ını ✅ yap
3. **Progress Track:** Phase progress'ini güncelle

### Session Template (Updated):
```
"Claude Code Task [From Project Plan]:

Task ID: [e.g., 2.1.1]
PRD Reference: [exact section from PRD.md]
Project Plan Instruction: [copy exact instruction from projectplan.md]
Expected Deliverable: [from project plan]
Validation Criteria: [from project plan]
Current Phase Progress: [X/Y tasks completed]

Context: Önceki tamamlanan tasks: [list completed task IDs]
Dependencies: [list prerequisite tasks that must be completed]"
```

### Example Session Call:
```
"Claude Code Task [From Project Plan]:

Task ID: 2.1.1
PRD Reference: Algorithm 1: Address Validator
Project Plan Instruction: PRD'deki AddressValidator spec'ine göre tests/test_address_validator.py oluştur
Expected Deliverable: Complete test suite with fixtures
Validation Criteria: Tests run and fail appropriately (no implementation yet)
Current Phase Progress: 0/12 tasks completed in Phase 2

Context: Phase 1 completed (8/8 tasks ✅)
Dependencies: Task 1.3.1 (Pydantic models) must be completed"
```

### Updated Progress Tracking Integration:

**Project Plan Status → Workflow Decisions:**
- ✅ **Completed Task** → Move to next task in sequence  
- 🔄 **In Progress** → Continue current task, don't start new ones
- ❌ **Failed Task** → Debug mode, rework current task
- 🚫 **Blocked** → Skip to parallel task or wait for dependency

**New Task Categories Integration:**
- **External Data Tasks (1.4.x):** Prioritize data quality and validation
- **Robustness Tests (2.5.2):** Focus on edge case coverage
- **Enhanced Demo (5.1.1):** Emphasize user experience and visualization
- **Post-Kaggle Strategy:** Prepare for final hackathon adaptability

**Updated Session Template:**
```
"Claude Code Task [From Updated Project Plan]:

Task ID: [e.g., 1.4.1, 2.5.2, etc.]
PRD Reference: [exact section from PRD.md]
Project Plan Instruction: [copy exact instruction from updated projectplan.md]
Expected Deliverable: [from updated project plan]
Validation Criteria: [from updated project plan]
Current Phase Progress: [X/Y tasks completed - updated counts]

Context: External data dependencies and robustness requirements
Dependencies: [list prerequisite tasks including new data tasks]
Special Notes: [any specific requirements for new features]"
```

### Quality Gates with Project Plan:

**Phase Completion Gates:**
```python
def check_phase_completion(phase_number):
    """Project plan based phase completion check"""
    
    phase_tasks = get_phase_tasks(phase_number)
    completed_tasks = [task for task in phase_tasks if task.status == "✅"]
    failed_tasks = [task for task in phase_tasks if task.status == "❌"]
    
    if len(failed_tasks) > 0:
        return f"🔴 Phase {phase_number} has failed tasks: {failed_tasks}"
    
    if len(completed_tasks) == len(phase_tasks):
        return f"✅ Phase {phase_number} completed successfully"
    
    return f"🔄 Phase {phase_number} in progress: {len(completed_tasks)}/{len(phase_tasks)}"
```

### Risk Management Integration:

**Project Plan Risk Indicators → Workflow Actions:**
- 🟢 **Low Risk** → Continue normal workflow
- 🟡 **Medium Risk** → Add extra validation steps, more frequent checkpoints
- 🔴 **High Risk** → Stop and review, potentially restart failed phase

**Automated Risk Detection:**
```python
def calculate_project_risk():
    """Calculate risk based on project plan status"""
    
    total_tasks = count_all_tasks()
    failed_tasks = count_failed_tasks()
    blocked_tasks = count_blocked_tasks()
    
    risk_percentage = (failed_tasks + blocked_tasks) / total_tasks * 100
    
    if risk_percentage < 10:
        return "🟢 Low Risk"
    elif risk_percentage < 20:
        return "🟡 Medium Risk" 
    else:
        return "🔴 High Risk"
```