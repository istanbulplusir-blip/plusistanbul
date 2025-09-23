# Dark Mode Implementation Guide

## Overview

This guide explains how dark mode is implemented in the Peykan Tourism Platform and provides best practices for maintaining consistency across all components.

## Architecture

### Theme Context

- **File**: `lib/contexts/ThemeContext.tsx`
- **Purpose**: Centralized theme state management
- **Features**:
  - Automatic system preference detection
  - Local storage persistence
  - Hydration mismatch prevention
  - TypeScript support

### Theme Provider

- **Location**: `app/[locale]/layout.tsx`
- **Scope**: Wraps entire application
- **Usage**: Automatically available to all components

## Usage

### Basic Theme Hook

```tsx
import { useTheme } from "../lib/contexts/ThemeContext";

function MyComponent() {
  const { theme, toggleTheme, setTheme } = useTheme();

  return <button onClick={toggleTheme}>Current theme: {theme}</button>;
}
```

### Theme-Aware Styling

```tsx
// ✅ Good: Use dark: variants
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content
</div>

// ❌ Bad: Fixed colors
<div className="bg-white text-black">
  Content
</div>
```

## Color System

### Background Colors

```tsx
// Primary backgrounds
bg-white dark:bg-gray-900          // Main page background
bg-white dark:bg-gray-800          // Card backgrounds
bg-gray-50 dark:bg-gray-800        // Secondary backgrounds
bg-gray-100 dark:bg-gray-700       // Tertiary backgrounds

// Overlay backgrounds
bg-black/50 dark:bg-black/70       // Modal overlays
bg-white/20 dark:bg-white/10       // Semi-transparent overlays
```

### Text Colors

```tsx
// Primary text
text-gray-900 dark:text-white      // Main headings
text-gray-700 dark:text-gray-300   // Body text
text-gray-600 dark:text-gray-400   // Secondary text
text-gray-500 dark:text-gray-500   // Muted text

// Interactive text
text-blue-600 dark:text-blue-400   // Links and primary actions
text-green-600 dark:text-green-400 // Success states
text-red-600 dark:text-red-400     // Error states
```

### Border Colors

```tsx
// Standard borders
border-gray-200 dark:border-gray-700  // Primary borders
border-gray-100 dark:border-gray-700  // Secondary borders
border-transparent                     // No border
```

### Interactive States

```tsx
// Hover states
hover:bg-gray-50 dark:hover:bg-gray-700
hover:bg-gray-100 dark:hover:bg-gray-600
hover:bg-blue-50 dark:hover:bg-blue-900/20

// Focus states
focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900
```

## Component Patterns

### Cards

```tsx
// Standard card
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
    Card Title
  </h3>
  <p className="text-gray-600 dark:text-gray-300">Card content</p>
</div>
```

### Buttons

```tsx
// Primary button
<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
  Primary Action
</button>

// Secondary button
<button className="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600">
  Secondary Action
</button>

// Ghost button
<button className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 px-4 py-2 rounded-lg">
  Ghost Action
</button>
```

### Forms

```tsx
// Input fields
<input
  className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800"
  placeholder="Enter text..."
/>

// Labels
<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
  Field Label
</label>

// Error messages
<p className="text-sm text-red-600 dark:text-red-400">
  Error message
</p>
```

### Modals

```tsx
// Modal overlay
<div className="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50">
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
    {/* Modal content */}
  </div>
</div>
```

## Best Practices

### 1. Always Use Dark Variants

- Every component should have `dark:` variants for all colors
- Never use fixed colors like `bg-white` or `text-black` without dark alternatives

### 2. Consistent Color Mapping

- Light backgrounds → Dark backgrounds
- Dark text → Light text
- Maintain proper contrast ratios (WCAG AA compliance)

### 3. Interactive States

- Hover, focus, and active states should work in both themes
- Use opacity-based overlays for consistent behavior

### 4. Icon Colors

- Icons should adapt to the current theme
- Use semantic colors when appropriate (e.g., `text-blue-500` for info icons)

### 5. Gradients and Images

- Gradients should work in both themes
- Image overlays should use appropriate opacity values
- Text over images should have proper contrast

### 6. Transitions

- Use consistent transition durations (`transition-all duration-300`)
- Smooth theme switching with `transition-colors`

## Common Patterns

### Section Backgrounds

```tsx
<section className="py-20 bg-white dark:bg-gray-900">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {/* Section content */}
  </div>
</section>
```

### Grid Items

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map((item) => (
    <div
      key={item.id}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
    >
      {/* Item content */}
    </div>
  ))}
</div>
```

### Navigation Items

```tsx
<Link
  href="/path"
  className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
>
  Navigation Link
</Link>
```

## Testing Dark Mode

### Manual Testing

1. Toggle dark mode using the navbar button
2. Check all components render correctly
3. Verify text readability and contrast
4. Test interactive states (hover, focus, active)
5. Ensure modals and overlays work properly

### Automated Testing

- Use browser dev tools to simulate dark mode
- Test with different system preferences
- Verify color contrast ratios meet accessibility standards

## Troubleshooting

### Common Issues

1. **Hydration Mismatch**

   - Ensure ThemeProvider handles mounted state
   - Use conditional rendering for theme-dependent content

2. **Missing Dark Variants**

   - Check all color classes have `dark:` alternatives
   - Use grep search: `bg-white|text-black|bg-black` (without dark variants)

3. **Inconsistent Colors**

   - Follow the established color system
   - Use design tokens when available
   - Maintain semantic meaning across themes

4. **Performance Issues**
   - Avoid excessive `dark:` variants
   - Use CSS custom properties for complex themes
   - Minimize re-renders during theme switching

## Migration Guide

### Converting Existing Components

1. **Identify Fixed Colors**

   ```tsx
   // Before
   <div className="bg-white text-black">

   // After
   <div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
   ```

2. **Update Interactive States**

   ```tsx
   // Before
   <button className="hover:bg-gray-100">

   // After
   <button className="hover:bg-gray-100 dark:hover:bg-gray-700">
   ```

3. **Add Dark Variants for Borders**

   ```tsx
   // Before
   <div className="border border-gray-200">

   // After
   <div className="border border-gray-200 dark:border-gray-700">
   ```

## Resources

- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [WCAG Color Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Design System Tokens](./lib/design-system/tokens/colors.ts)
- [Component Library](./components/ui/)

## Support

For questions or issues with dark mode implementation:

1. Check this guide first
2. Review existing components for patterns
3. Ensure consistency with the established color system
4. Test thoroughly in both themes before committing
