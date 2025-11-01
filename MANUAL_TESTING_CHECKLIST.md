# 📋 Manual Testing Checklist
## Static Pages Fix - Task 7 Validation

**Purpose:** This checklist helps you manually validate the Privacy and Terms pages implementation.  
**Estimated Time:** 30-45 minutes  
**Prerequisites:** Development server running or staging deployment

---

## 🚀 Getting Started

### Start the Development Server
```bash
cd plusistanbul/frontend
npm run dev
```

The application should be available at: `http://localhost:3000`

---

## ✅ Testing Checklist

### 1. 🌐 Browser Testing (8 tests)

#### Chrome
- [ ] Open `http://localhost:3000/fa/privacy` in Chrome
- [ ] Verify page loads without errors
- [ ] Open browser console (F12) - check for errors
- [ ] Navigate to `http://localhost:3000/fa/terms`
- [ ] Verify page loads without errors
- [ ] Check console for IntlError messages
- [ ] Test language switcher (switch to EN, then TR)
- [ ] Verify smooth navigation

**Notes:**
```
Chrome Version: _____________
Issues Found: _______________
_____________________________
```

#### Firefox
- [ ] Open `http://localhost:3000/en/privacy` in Firefox
- [ ] Verify page loads without errors
- [ ] Open browser console (F12) - check for errors
- [ ] Navigate to `http://localhost:3000/en/terms`
- [ ] Verify page loads without errors
- [ ] Check console for IntlError messages
- [ ] Test language switcher
- [ ] Verify smooth navigation

**Notes:**
```
Firefox Version: ____________
Issues Found: _______________
_____________________________
```

#### Safari (if available)
- [ ] Open `http://localhost:3000/tr/privacy` in Safari
- [ ] Verify page loads without errors
- [ ] Open browser console - check for errors
- [ ] Navigate to `http://localhost:3000/tr/terms`
- [ ] Verify page loads without errors
- [ ] Check console for IntlError messages
- [ ] Test language switcher
- [ ] Verify smooth navigation

**Notes:**
```
Safari Version: _____________
Issues Found: _______________
_____________________________
```

---

### 2. 🌍 Language Testing (6 tests)

#### Persian (فارسی)
- [ ] Navigate to `/fa/privacy`
- [ ] Verify title is in Persian: "سیاست حفظ حریم خصوصی"
- [ ] Verify all content sections display in Persian
- [ ] Verify CTA button text is in Persian
- [ ] Navigate to `/fa/terms`
- [ ] Verify title is in Persian: "شرایط خدمات"
- [ ] Verify all content sections display in Persian
- [ ] Verify CTA button text is in Persian

**Content Verification:**
```
Privacy Title: ☐ Correct ☐ Incorrect
Terms Title:   ☐ Correct ☐ Incorrect
All Sections:  ☐ Persian ☐ Mixed ☐ English
```

#### English
- [ ] Navigate to `/en/privacy`
- [ ] Verify title is "Privacy Policy"
- [ ] Verify all content sections display in English
- [ ] Verify CTA button text is in English
- [ ] Navigate to `/en/terms`
- [ ] Verify title is "Terms of Service"
- [ ] Verify all content sections display in English
- [ ] Verify CTA button text is in English

**Content Verification:**
```
Privacy Title: ☐ Correct ☐ Incorrect
Terms Title:   ☐ Correct ☐ Incorrect
All Sections:  ☐ English ☐ Mixed ☐ Other
```

#### Turkish (Türkçe)
- [ ] Navigate to `/tr/privacy`
- [ ] Verify title is "Gizlilik Politikası"
- [ ] Verify all content sections display in Turkish
- [ ] Verify CTA button text is in Turkish
- [ ] Navigate to `/tr/terms`
- [ ] Verify title is "Hizmet Şartları"
- [ ] Verify all content sections display in Turkish
- [ ] Verify CTA button text is in Turkish

**Content Verification:**
```
Privacy Title: ☐ Correct ☐ Incorrect
Terms Title:   ☐ Correct ☐ Incorrect
All Sections:  ☐ Turkish ☐ Mixed ☐ Other
```

---

### 3. 🦶 Footer Testing (5 tests)

#### Privacy Page
- [ ] Scroll to bottom of `/fa/privacy`
- [ ] Verify Footer is visible
- [ ] Check Footer has all sections (About, Contact, Privacy, Terms, etc.)
- [ ] Click on "Contact" link in Footer
- [ ] Verify navigation works

**Footer Checklist:**
```
☐ Footer visible
☐ All links present
☐ Links functional
☐ Social media icons present
☐ Newsletter form present
```

#### Terms Page
- [ ] Scroll to bottom of `/fa/terms`
- [ ] Verify Footer is visible
- [ ] Check Footer has all sections
- [ ] Click on "About" link in Footer
- [ ] Verify navigation works

#### Other Static Pages
- [ ] Navigate to `/fa/faq` - verify Footer
- [ ] Navigate to `/fa/about` - verify Footer
- [ ] Navigate to `/fa/contact` - verify Footer

**Notes:**
```
Issues Found: _______________
_____________________________
_____________________________
```

---

### 4. 🌓 Theme Testing (8 tests)

#### Light Mode - Privacy Page
- [ ] Ensure light mode is active (check theme toggle)
- [ ] Navigate to `/fa/privacy`
- [ ] Verify text is readable (dark text on light background)
- [ ] Check header gradient is visible
- [ ] Verify icon colors are appropriate
- [ ] Check content section backgrounds
- [ ] Verify CTA section contrast
- [ ] Scroll through entire page checking readability

**Light Mode Assessment:**
```
Text Readability:    ☐ Excellent ☐ Good ☐ Poor
Background Colors:   ☐ Correct ☐ Issues
Icon Colors:         ☐ Correct ☐ Issues
Overall Contrast:    ☐ Good ☐ Needs Work
```

#### Dark Mode - Privacy Page
- [ ] Switch to dark mode (click theme toggle)
- [ ] Verify page updates to dark theme
- [ ] Check text is readable (light text on dark background)
- [ ] Verify background colors changed appropriately
- [ ] Check icon colors (should be lighter variants)
- [ ] Verify content section backgrounds (dark variants)
- [ ] Check CTA section in dark mode
- [ ] Scroll through entire page checking readability

**Dark Mode Assessment:**
```
Text Readability:    ☐ Excellent ☐ Good ☐ Poor
Background Colors:   ☐ Correct ☐ Issues
Icon Colors:         ☐ Correct ☐ Issues
Overall Contrast:    ☐ Good ☐ Needs Work
```

#### Light Mode - Terms Page
- [ ] Switch back to light mode
- [ ] Navigate to `/fa/terms`
- [ ] Verify text is readable
- [ ] Check all sections for proper contrast
- [ ] Verify icon colors
- [ ] Check CTA section

#### Dark Mode - Terms Page
- [ ] Switch to dark mode
- [ ] Verify page updates correctly
- [ ] Check text readability
- [ ] Verify all sections have proper dark backgrounds
- [ ] Check icon colors
- [ ] Verify CTA section

**Notes:**
```
Dark Mode Issues: ___________
_____________________________
_____________________________
```

---

### 5. 📱 Responsive Design Testing (5 tests)

#### Desktop (1920x1080)
- [ ] Open browser in full screen
- [ ] Navigate to `/fa/privacy`
- [ ] Verify layout looks good
- [ ] Check content width (should be constrained, not full width)
- [ ] Verify spacing is appropriate
- [ ] Navigate to `/fa/terms`
- [ ] Verify layout consistency

**Desktop Assessment:**
```
Layout:        ☐ Excellent ☐ Good ☐ Issues
Spacing:       ☐ Appropriate ☐ Too tight ☐ Too loose
Content Width: ☐ Good ☐ Too wide ☐ Too narrow
```

#### Tablet (768x1024)
- [ ] Resize browser to 768px width (or use device toolbar F12)
- [ ] Navigate to `/fa/privacy`
- [ ] Verify layout adapts properly
- [ ] Check text remains readable
- [ ] Verify buttons are touch-friendly
- [ ] Navigate to `/fa/terms`
- [ ] Verify layout consistency

**Tablet Assessment:**
```
Layout:        ☐ Excellent ☐ Good ☐ Issues
Touch Targets: ☐ Good size ☐ Too small
Readability:   ☐ Good ☐ Issues
```

#### Mobile (375x667)
- [ ] Resize browser to 375px width
- [ ] Navigate to `/fa/privacy`
- [ ] Verify layout stacks properly
- [ ] Check text is readable (not too small)
- [ ] Verify buttons are large enough
- [ ] Test scrolling behavior
- [ ] Navigate to `/fa/terms`
- [ ] Verify layout consistency

**Mobile Assessment:**
```
Layout:        ☐ Excellent ☐ Good ☐ Issues
Text Size:     ☐ Good ☐ Too small ☐ Too large
Buttons:       ☐ Good size ☐ Too small
Scrolling:     ☐ Smooth ☐ Issues
```

#### Small Mobile (320x568)
- [ ] Resize browser to 320px width
- [ ] Navigate to `/fa/privacy`
- [ ] Verify content doesn't overflow
- [ ] Check text remains readable
- [ ] Navigate to `/fa/terms`
- [ ] Verify layout works

#### Real Device Testing (if available)
- [ ] Test on actual smartphone
- [ ] Test on actual tablet
- [ ] Verify touch interactions work

**Notes:**
```
Device Tested: ______________
Issues Found: _______________
_____________________________
```

---

### 6. 🎨 UI/UX Consistency Testing (6 tests)

#### Compare Privacy with Contact Page
- [ ] Open `/fa/privacy` and `/fa/contact` in separate tabs
- [ ] Compare header section styling
- [ ] Compare content section styling
- [ ] Compare icon usage and placement
- [ ] Compare color schemes
- [ ] Compare spacing and typography

**Consistency Check:**
```
Header:     ☐ Consistent ☐ Different
Content:    ☐ Consistent ☐ Different
Icons:      ☐ Consistent ☐ Different
Colors:     ☐ Consistent ☐ Different
Spacing:    ☐ Consistent ☐ Different
Typography: ☐ Consistent ☐ Different
```

#### Compare Terms with About Page
- [ ] Open `/fa/terms` and `/fa/about` in separate tabs
- [ ] Compare overall layout
- [ ] Compare styling consistency
- [ ] Compare navigation elements
- [ ] Compare footer styling

#### Compare with Catalog Page
- [ ] Open `/fa/privacy` and `/fa/catalog` in separate tabs
- [ ] Verify Footer is consistent
- [ ] Check navigation consistency
- [ ] Verify overall design language matches

**Notes:**
```
Inconsistencies Found: ______
_____________________________
_____________________________
```

---

### 7. 🔗 Navigation Testing (8 tests)

#### Footer Links
- [ ] Click "Privacy" link in Footer (from any page)
- [ ] Verify navigates to Privacy page
- [ ] Click "Terms" link in Footer
- [ ] Verify navigates to Terms page
- [ ] Click "Contact" link in Footer
- [ ] Verify navigates to Contact page
- [ ] Click "About" link in Footer
- [ ] Verify navigates to About page

**Link Functionality:**
```
☐ All links work
☐ Some links broken (specify): ___________
☐ Navigation smooth
☐ Navigation issues
```

#### CTA Buttons
- [ ] On Privacy page, click CTA button
- [ ] Verify navigates to Contact page
- [ ] Go back to Privacy page
- [ ] On Terms page, click CTA button
- [ ] Verify navigates to Contact page

#### Language Switcher
- [ ] On Privacy page, switch from FA to EN
- [ ] Verify stays on Privacy page (URL changes to /en/privacy)
- [ ] Switch from EN to TR
- [ ] Verify stays on Privacy page (URL changes to /tr/privacy)
- [ ] Repeat for Terms page

#### Browser Navigation
- [ ] Navigate through several pages
- [ ] Click browser back button
- [ ] Verify goes to previous page correctly
- [ ] Click browser forward button
- [ ] Verify goes forward correctly

**Notes:**
```
Navigation Issues: __________
_____________________________
_____________________________
```

---

### 8. 📄 Content Validation (13 tests)

#### Privacy Page Content Sections
- [ ] **Introduction:** Verify text displays
- [ ] **Data Collection:** Verify section with Database icon
- [ ] **Data Usage:** Verify section with Shield icon
- [ ] **Data Security:** Verify section with Lock icon
- [ ] **User Rights:** Verify section with UserCheck icon
- [ ] **Contact:** Verify section with Mail icon
- [ ] Verify all icons display correctly
- [ ] Verify all text is properly formatted
- [ ] Verify no placeholder text (Lorem ipsum, etc.)

**Privacy Content Check:**
```
☐ All sections present
☐ All icons display
☐ Text properly formatted
☐ No placeholders
☐ Content makes sense
```

#### Terms Page Content Sections
- [ ] **Introduction:** Verify text displays
- [ ] **Acceptance:** Verify section with FileCheck icon
- [ ] **Services:** Verify section with Briefcase icon
- [ ] **Booking Policy:** Verify section with Calendar icon
- [ ] **Cancellation Policy:** Verify section with XCircle icon
- [ ] **Liability:** Verify section with AlertTriangle icon
- [ ] **Changes:** Verify section with RefreshCw icon
- [ ] Verify all icons display correctly
- [ ] Verify all text is properly formatted
- [ ] Verify no placeholder text

**Terms Content Check:**
```
☐ All sections present
☐ All icons display
☐ Text properly formatted
☐ No placeholders
☐ Content makes sense
```

---

## 📊 Test Summary

### Overall Results
```
Total Tests Completed: _____ / 59
Tests Passed:          _____ 
Tests Failed:          _____
Critical Issues:       _____
Minor Issues:          _____
```

### Critical Issues Found
```
1. _____________________________
2. _____________________________
3. _____________________________
```

### Minor Issues Found
```
1. _____________________________
2. _____________________________
3. _____________________________
```

### Recommendations
```
1. _____________________________
2. _____________________________
3. _____________________________
```

---

## ✅ Sign-Off

### Tester Information
```
Name:     _______________________
Date:     _______________________
Time:     _______________________
Browser:  _______________________
OS:       _______________________
```

### Approval
```
☐ All tests passed - Ready for production
☐ Minor issues found - Can deploy with notes
☐ Critical issues found - Needs fixes before deployment
```

### Notes
```
_________________________________
_________________________________
_________________________________
_________________________________
```

---

## 📚 Additional Resources

- **Automated Test Report:** `STATIC_PAGES_TEST_REPORT.md`
- **Completion Summary:** `TASK_7_COMPLETION_SUMMARY.md`
- **Visual Results:** `TESTING_RESULTS_VISUAL.md`
- **Test Script:** `test_static_pages_final.js`

---

## 🆘 Troubleshooting

### If pages don't load:
1. Check if development server is running
2. Check console for errors
3. Verify correct URL format: `/[locale]/[page]`
4. Try clearing browser cache

### If translations are missing:
1. Check browser console for IntlError
2. Verify translation files exist in `frontend/messages/`
3. Check language code is correct (fa, en, tr)

### If Footer doesn't appear:
1. Scroll to bottom of page
2. Check if `showFooter` prop is set correctly
3. Verify Footer component is imported

---

*Manual Testing Checklist - Task 7*  
*Generated: November 1, 2025*
