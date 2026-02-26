# Advanced Search Implementation Plan

## Task Summary
Create an advanced search page with comprehensive filtering and sorting capabilities for the document library.

## Features to Implement

### Left Side (Filters Panel)
- [ ] Title keyword search
- [ ] Author search (including Book authors)
- [ ] Document type filter
- [ ] Category filter
- [ ] Year range (From – To)
- [ ] Committee / Department filter
- [ ] Language filter
- [ ] Date uploaded filter

### Top Right
- [ ] Sort by: Newest, Oldest, Title A–Z, Most downloaded

### Main Area
- [ ] Search results display
- [ ] Pagination
- [ ] Result count display

## Files to Modify

### 1. documents/forms.py
- Add new fields to DocumentSearchForm:
  - year_from, year_to (for year range)
  - committee (committee_name filter)
  - language
  - date_from, date_to (date uploaded range)

### 2. documents/views.py
- Update document_list view to:
  - Handle all new filter parameters
  - Implement sorting options (newest, oldest, title A-Z, most downloaded)
  - Include Book model author search
  - Handle year range filtering

### 3. templates/documents/document_list.html
- Redesign layout with filters on left, results on right
- Add all filter controls
- Add sorting dropdown
- Add result count and pagination

## Implementation Order
1. Update forms.py with new search form fields
2. Update views.py with new filtering and sorting logic
3. Update template with new layout and controls
4. Test the implementation

