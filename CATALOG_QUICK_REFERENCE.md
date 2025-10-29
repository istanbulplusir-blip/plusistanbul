# PDF Catalog - Quick Reference Guide

## 🎯 Quick Links

- **Frontend Page:** http://localhost:3000/fa/catalog
- **API Endpoint:** http://localhost:8000/api/shared/catalogs/featured/
- **Admin Panel:** http://localhost:8000/admin/shared/catalogfile/
- **Direct PDF:** http://localhost:8000/media/catalogs/Peykan%20Travel%20Tour-Guide-2025-1.pdf

## 📁 Key Files

### Backend
- **Model:** `plusistanbul/backend/shared/models.py` (CatalogFile class)
- **ViewSet:** `plusistanbul/backend/shared/views.py` (CatalogFileViewSet class)
- **Serializer:** `plusistanbul/backend/shared/serializers.py` (CatalogFileSerializer class)
- **Admin:** `plusistanbul/backend/shared/admin.py` (CatalogFileAdmin class)
- **URLs:** `plusistanbul/backend/shared/urls.py` (router registration)

### Frontend
- **Page:** `plusistanbul/frontend/app/[locale]/catalog/page.tsx`
- **Component:** `plusistanbul/frontend/components/catalog/CatalogViewer.tsx`
- **Translations:** `plusistanbul/frontend/messages/{fa,en,tr}.json`

## 🚀 Quick Start

### View the Catalog Page
```bash
# Start backend
cd plusistanbul/backend
python3 manage.py runserver

# Start frontend (in another terminal)
cd plusistanbul/frontend
npm run dev

# Open in browser
http://localhost:3000/fa/catalog
```

### Test API Directly
```bash
# Get featured catalog
curl http://localhost:8000/api/shared/catalogs/featured/

# List all catalogs
curl http://localhost:8000/api/shared/catalogs/

# Track view (replace {id} with catalog ID)
curl -X POST http://localhost:8000/api/shared/catalogs/{id}/track_view/
```

### Access Admin Panel
```bash
# Open admin
http://localhost:8000/admin/shared/catalogfile/

# Login with your admin credentials
# View/edit catalogs
```

## 📊 Current Status

- ✅ 1 catalog in database: "راهنمای تورهای پیکان ترول ۲۰۲۵"
- ✅ Featured: Yes
- ✅ File: Peykan Travel Tour-Guide-2025-1.pdf (13MB)
- ✅ View count: 2
- ✅ Download count: 2

## 🧪 Run Tests

### Automated Tests
```bash
cd plusistanbul
python3 test_catalog_integration.py
```

### Manual Tests
```bash
cd plusistanbul
./test_catalog_manual.sh
```

## 📝 Common Tasks

### Add a New Catalog
1. Go to admin: http://localhost:8000/admin/shared/catalogfile/
2. Click "Add Catalog File"
3. Fill in:
   - Title (in all languages)
   - Description (optional)
   - Upload PDF file (max 50MB)
   - Select catalog type
   - Set version
   - Check "Is featured" if this should be the default
4. Save

### Update Existing Catalog
1. Go to admin: http://localhost:8000/admin/shared/catalogfile/
2. Click on the catalog to edit
3. Update fields or upload new PDF
4. Save

### Check Analytics
1. Go to admin: http://localhost:8000/admin/shared/catalogfile/
2. View "Download count" and "View count" columns
3. Click on a catalog to see detailed stats

## 🌐 Multi-Language URLs

- **Persian:** http://localhost:3000/fa/catalog
- **English:** http://localhost:3000/en/catalog
- **Turkish:** http://localhost:3000/tr/catalog

## 📱 Mobile Testing

1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select device (iPhone, Android)
4. Navigate to catalog page
5. Test:
   - PDF viewer displays
   - Fixed download button at bottom
   - Responsive layout
   - Touch interactions

## 🔗 WhatsApp Integration

### Direct PDF Link
```
https://peykantravelistanbul.com/media/catalogs/Peykan Travel Tour-Guide-2025-1.pdf
```

### Catalog Page Link
```
https://peykantravelistanbul.com/fa/catalog
```

### Sample WhatsApp Message
```
سلام! 👋

کاتالوگ کامل تورهای ما را مشاهده کنید:
https://peykantravelistanbul.com/fa/catalog

یا مستقیماً دانلود کنید:
https://peykantravelistanbul.com/media/catalogs/Peykan Travel Tour-Guide-2025-1.pdf

برای رزرو با ما تماس بگیرید! 📞
```

## 🐛 Troubleshooting

### PDF Not Loading
- Check if backend server is running
- Verify file exists: `ls -lh plusistanbul/backend/media/catalogs/`
- Check API response: `curl http://localhost:8000/api/shared/catalogs/featured/`

### 404 Error on Catalog Page
- Check if frontend server is running
- Verify route exists: `plusistanbul/frontend/app/[locale]/catalog/page.tsx`
- Check browser console for errors

### Download Button Not Working
- Check if catalog has `download_url` in API response
- Verify file URL is accessible
- Check browser console for errors

### Translations Missing
- Verify translation keys exist in `messages/{locale}.json`
- Check `catalog` object has all required keys
- Restart frontend server after translation changes

## 📚 Documentation

- **Detailed Test Report:** `CATALOG_TEST_REPORT.md`
- **Integration Summary:** `CATALOG_INTEGRATION_TEST_SUMMARY.md`
- **Requirements:** `.kiro/specs/pdf-catalog-display-download/requirements.md`
- **Design:** `.kiro/specs/pdf-catalog-display-download/design.md`
- **Tasks:** `.kiro/specs/pdf-catalog-display-download/tasks.md`

## ✅ Verification Checklist

Quick checklist to verify everything is working:

- [ ] Backend server running
- [ ] Frontend server running
- [ ] Catalog page loads (all 3 languages)
- [ ] PDF displays in viewer
- [ ] Download button works
- [ ] Mobile responsive
- [ ] Analytics tracking works
- [ ] Admin panel accessible
- [ ] Direct PDF URL works

## 🎉 Success!

If all items in the checklist are checked, the PDF Catalog feature is fully functional!

---

**Need Help?** Check the detailed documentation files or run the test scripts.
