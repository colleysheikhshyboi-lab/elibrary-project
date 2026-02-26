# Document Upload Fix - TODO

## Problem
- Uploaded documents are not visible after upload
- Root cause: Documents are saved with `is_published=False` (default), but the list view only shows `is_published=True`
- Additional issue: Missing Django permissions for document operations

## Fix Plan

### Step 1: Fix document_list view (documents/views.py)
- Show unpublished documents to users who can upload
- Users with `can_upload` permission should see all their uploaded documents (published and unpublished)

### Step 2: Add missing permissions (documents/models.py)
- Add `add_document`, `change_document`, `delete_document`, `view_document` permissions to Document model's Meta class

## Status
- [x] Step 1: Update document_list view
- [x] Step 2: Add permissions to Document model (Skipped - built-in permissions conflict)

## Additional Notes
- Django built-in permissions (`add_document`, `change_document`, `delete_document`, `view_document`) already exist for models
- The views using `@permission_required` will work because Django auto-generates these permissions
- Tests pass successfully

