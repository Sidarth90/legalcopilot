# LegalCopilot - Technical Specifications

## 🎯 Product Requirements Document (PRD)

### **Core Functionality**
- **PDF Contract Analysis**: Upload PDF contracts and get AI-powered clause explanations
- **Interactive Highlighting**: Click clauses to see detailed risk analysis and implications
- **Auto-Navigation**: Automatic scrolling to clause locations in document
- **Page-by-Page View**: HTML display matches original PDF page structure exactly

### **User Experience Requirements**

#### **Critical UX Rule: Page Layout Consistency**
- ✅ **HTML viewer must mirror PDF page structure**
- ✅ **Users should not feel lost between PDF and HTML versions**
- ✅ **Each page displays content exactly as in original PDF**
- ✅ **Clear page boundaries with distinct page headers**
- ✅ **Maintain original content distribution per page**

#### **Navigation Requirements**
- Auto-scroll to exact clause location on click
- Visual feedback (2-second flash effect) on scroll target
- Smooth scrolling animation for better UX
- Fallback search by article number if primary target fails

#### **Highlighting Standards**
- **SEMANTIC ONLY**: No random keyword highlighting
- **CONTEXTUAL**: Only highlight actual legal clause structures
- **CONFIDENCE-BASED**: High confidence matches only (>80%)
- **VISUAL FEEDBACK**: Clear risk level indicators (HIGH/MEDIUM/LOW)

## 🔧 Technical Architecture

### **Frontend Stack**
- **PDF.js**: PDF parsing and text extraction
- **Vanilla JavaScript**: No framework dependencies
- **Modern CSS**: Tailwind-inspired styling
- **Responsive Design**: Three-panel layout (20-50-30)

### **Backend Stack**
- **Flask**: Python web server (localhost:5001)
- **PyPDF2**: Server-side PDF processing
- **CORS**: Cross-origin resource sharing for local files
- **Enhanced Pattern Matching**: Semantic legal clause detection

### **AI Integration**
- **Deepseek API**: Primary AI analysis (when available)
- **Pattern Fallback**: Sophisticated regex patterns as backup
- **Confidence Scoring**: 0.8-0.95 confidence thresholds
- **Risk Assessment**: Automated HIGH/MEDIUM/LOW classification

## 🎨 UI/UX Specifications

### **Layout Structure**
```
┌─────────────────────────────────────────────────────────┐
│                    Header (Brand)                       │
├───────────────┬─────────────────────────┬───────────────┤
│   Clause      │      Document           │    Clause     │
│   List        │      Viewer             │    Details    │
│   (20%)       │      (50%)              │    (30%)      │
│               │                         │               │
│ - Governance  │  ┌─────────────────┐   │ ┌───────────┐ │
│ - Drag Along  │  │     Page 1      │   │ │   Risk    │ │
│ - Tag Along   │  │                 │   │ │ Analysis  │ │
│ - Priority    │  │   [Content]     │   │ │           │ │
│ - Non-Compete │  │                 │   │ │ Context   │ │
│               │  └─────────────────┘   │ │           │ │
│               │  ┌─────────────────┐   │ │ Implica-  │ │
│               │  │     Page 2      │   │ │ tions     │ │
│               │  │                 │   │ └───────────┘ │
│               │  │   [Content]     │   │               │
└───────────────┴─────────────────────────┴───────────────┘
```

### **Page Display Standards**
- **Page Headers**: Distinct visual separation with page numbers
- **Content Boundaries**: Clear borders around each page
- **Scroll Behavior**: Smooth scrolling within document area
- **Visual Hierarchy**: Highlighted clauses stand out clearly

## 🤖 AI Analysis Specifications

### **Semantic Patterns**
```javascript
// Example: Drag-Along Rights Detection
semanticPattern: /drag.?along\s+right|ninety.five\s+per\s+cent.*shares|95%.*shareholders.*sell/gi
fullClausePattern: /1\.5[^0-9]*drag.?along[^.]*\./gi
```

### **Detection Logic**
1. **Context Analysis**: Understand legal clause structure
2. **Pattern Matching**: Multi-pattern semantic recognition
3. **Confidence Scoring**: Weighted confidence calculation
4. **Risk Assessment**: Automated classification based on clause type
5. **Location Tracking**: Store scroll targets for navigation

### **Clause Categories**
- **Governance Compromise**: Voting control limitations
- **Drag-Along Rights**: Forced sale provisions
- **Tag-Along Rights**: Minority protection mechanisms
- **Priority Allocation**: Liquidation waterfalls
- **Non-Compete**: Survival provisions

## 🔄 Development Workflow

### **Testing Protocol**
1. **QA Video Recording**: 20-40 second interaction recordings
2. **Frame Extraction**: 8 frames per video for analysis
3. **Automated QA Reports**: HTML summaries with issue detection
4. **Console Logging**: Detailed debugging output for issues

### **Deployment Standards**
- **Local Development**: Flask server on localhost:5001
- **File Structure**: Standalone HTML files for easy distribution
- **Cross-Browser**: Chrome/Edge/Firefox compatibility
- **Performance**: <2 second load times for 31-page documents

## 📊 Performance Requirements

### **Loading Standards**
- **PDF Processing**: <10 seconds for 31-page documents
- **Chunk Processing**: 5-page batches with 100ms delays
- **Memory Management**: No browser crashes on large documents
- **Visual Feedback**: Progress indicators during processing

### **Interaction Standards**
- **Click Response**: <500ms clause selection response
- **Scroll Animation**: 800ms smooth scroll duration
- **Visual Feedback**: 2-second flash effects
- **Error Handling**: Graceful fallbacks for all scenarios

## 🚨 Critical Issues to Avoid

### **Layout Issues**
- ❌ Content merged across pages
- ❌ Lost page boundaries
- ❌ Inconsistent spacing
- ❌ Mobile responsiveness breaking

### **Functionality Issues**
- ❌ Auto-scroll not working
- ❌ Random keyword highlighting
- ❌ Backend connection failures
- ❌ Missing visual feedback

### **User Experience Issues**
- ❌ Users feeling lost between PDF/HTML
- ❌ Unclear clause highlighting
- ❌ Slow response times
- ❌ Broken interactive elements

---

**Document Version**: 1.0 - January 2025  
**Last Updated**: After semantic clause detection implementation  
**Status**: Living document - update after each major feature