# AMS JobAssist - Trainer Dashboard Frontend

Complete web UI for Tool 2 Trainer Dashboard. Single-page application (SPA) built with vanilla JavaScript, HTML5, and CSS3.

## Files

- **index.html** - Main application shell with all view sections
- **styles.css** - Complete styling with responsive design
- **js/api.js** - API client wrapper for backend communication
- **js/state.js** - Client-side state management
- **js/components.js** - Reusable UI components
- **js/app.js** - Main application logic and view routing

## Features Implemented

### Dashboard View
- Metrics cards (total participants, completed, avg quality, pending)
- Cohort selector
- Recent activity feed
- Quick action buttons (Import, Export)

### Participants View
- Searchable, filterable participant list
- Status filtering (pending, approved, rejected, needs_changes)
- Cohort filtering
- Bulk actions (approve, reject, export)
- Table showing: Name, Email, Status, Quality, Last Updated, Actions

### Detail View
- Participant header with contact info and status
- Side-by-side CV comparison (Original Answers | Polished CV)
- Inline editing of polished CV sections
- Approval workflow (status dropdown, trainer notes, save button)
- Click-to-edit sections with save/cancel

### Import View
- Drag-and-drop file upload
- Support for .json and .zip files
- Cohort selection
- Import progress and success/error messages

### Settings View
- Trainer name configuration
- Export preferences (language, format)
- Cache clearing
- System information

## How It Works

### Architecture
1. **Single Page App (SPA)**: All navigation handled by JavaScript
2. **API-First**: All data comes from backend API endpoints
3. **State Management**: Centralized client state in `appState` object
4. **Event-Driven UI**: Changes trigger DOM updates

### Data Flow
```
User Action → Event Listener → API Call → State Update → DOM Render
```

### View Switching
- Navigation buttons switch between views
- Views are hidden/shown with CSS `display` and `active` class
- Each view loads its own data when activated

### API Endpoints Used
- `GET /api/participants` - List participants
- `GET /api/participants/{id}` - Get participant detail
- `POST /api/participants/{id}/approve` - Approve/reject submission
- `GET /api/cohorts/{id}/metrics` - Get cohort metrics
- `POST /api/import-cvs` - Import CVs (multipart file upload)
- `POST /api/bulk-export` - Export multiple CVs

## Installation & Running

1. Files are deployed to `tool-2-trainer-dashboard/frontend/`
2. Backend serves frontend via `http://localhost:8001/`
3. No build process needed - pure vanilla JavaScript

### Local Development
```bash
# Start backend
cd tool-2-trainer-dashboard/src/backend
python app.py

# Open browser
http://localhost:8001/
```

### Testing with Sample Data
1. Use Import view to import CVs from Tool 1
2. Or manually insert test data via API:
```bash
curl -X POST http://localhost:8001/api/import-cvs \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.json" \
  -F "cohort_id=Test-Cohort"
```

## Browser Support
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance
- Minimal dependencies (zero external libraries)
- Fast load time (all JS minifiable to <50KB)
- Smooth animations (CSS transitions)
- No page reloads (SPA benefits)

## Styling & Customization

### Color Scheme (in styles.css)
```css
--primary-color: #2563eb;      /* Blue */
--success-color: #16a34a;      /* Green */
--danger-color: #dc2626;       /* Red */
--text-primary: #1e293b;       /* Dark slate */
--bg-light: #f8fafc;           /* Very light gray */
```

### Responsive Breakpoints
- Desktop: Full layout (1400px max-width)
- Tablet: 1024px - Grid adjusts
- Mobile: <768px - Stack layout

## Known Limitations & TODO

### Phase 11.2 Complete Features
- ✅ Dashboard with metrics
- ✅ Participant list with filtering
- ✅ Detail view with CV comparison
- ✅ Inline editing (click to edit)
- ✅ Approval workflow
- ✅ Bulk actions
- ✅ Import form with drag-and-drop
- ✅ Settings page
- ✅ Responsive design

### Future Enhancements (Phase 11.3+)
- Pagination for large participant lists
- Export formats (PDF, DOCX)
- Keyboard shortcuts
- Dark mode
- Real-time notifications
- Audit log
- Advanced filtering/sorting
- Participant search with autocomplete

## Code Quality

### Patterns Used
- Class-based organization (TrainerApp, AppState, Components, TrainerAPI)
- Async/await for API calls
- Event delegation for dynamic elements
- CSS Grid/Flexbox for layout
- BEM-like class naming

### No External Dependencies
- No jQuery
- No React/Vue/Angular
- No CSS framework
- Plain vanilla JavaScript (ES6+)
- Direct DOM manipulation with modern APIs

## Integration with Tool 1

The frontend expects CVData objects from Tool 1 with structure:
```json
{
  "user_id": "user123",
  "background": "...",
  "experience": "...",
  "skills": "...",
  "education": "...",
  "languages": "...",
  "overall_quality": 0.85,
  "ready_for_export": true
}
```

## Debugging

### Browser Console
```javascript
appState            // View current state
appState.participants  // View loaded participants
app.switchView('detail')  // Programmatically switch views
```

### API Testing
```javascript
// Test API calls directly
api.listParticipants().then(console.log)
api.getCohortMetrics('Cohort-1').then(console.log)
```

## File Size
- index.html: ~15KB
- styles.css: ~25KB
- js/api.js: ~3KB
- js/state.js: ~5KB
- js/components.js: ~8KB
- js/app.js: ~18KB
- **Total: ~74KB** (uncompressed)

## License
MIT - Part of AMS JobAssist project
