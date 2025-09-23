# Design System - Peykan Tourism

A comprehensive design system for the Peykan Tourism e-commerce application, built with Next.js, Tailwind CSS, and React components.

## Table of Contents

1. [Design Tokens](#design-tokens)
2. [Typography](#typography)
3. [Spacing](#spacing)
4. [Colors](#colors)
5. [Components](#components)
6. [Layout Patterns](#layout-patterns)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)

## Design Tokens

### Color Palette

#### Primary Colors

```css
--color-primary-50: #eff6ff
--color-primary-100: #dbeafe
--color-primary-200: #bfdbfe
--color-primary-300: #93c5fd
--color-primary-400: #60a5fa
--color-primary-500: #3b82f6
--color-primary-600: #2563eb
--color-primary-700: #1d4ed8
--color-primary-800: #1e40af
--color-primary-900: #1e3a8a
```

#### Secondary Colors

```css
--color-secondary-50: #f8fafc
--color-secondary-100: #f1f5f9
--color-secondary-200: #e2e8f0
--color-secondary-300: #cbd5e1
--color-secondary-400: #94a3b8
--color-secondary-500: #64748b
--color-secondary-600: #475569
--color-secondary-700: #334155
--color-secondary-800: #1e293b
--color-secondary-900: #0f172a
```

#### Neutral Colors

```css
--color-neutral-50: #f9fafb
--color-neutral-100: #f3f4f6
--color-neutral-200: #e5e7eb
--color-neutral-300: #d1d5db
--color-neutral-400: #9ca3af
--color-neutral-500: #6b7280
--color-neutral-600: #4b5563
--color-neutral-700: #374151
--color-neutral-800: #1f2937
--color-neutral-900: #111827
```

#### Semantic Colors

```css
--color-success: #22c55e
--color-warning: #f59e0b
--color-error: #ef4444
--color-danger: #ef4444
--color-info: #3b82f6
```

### Typography Scale

#### Headings

```css
/* H1 - Page titles */
.text-4xl md:text-5xl font-bold

/* H2 - Section titles */
.text-2xl font-bold

/* H3 - Subsection titles */
.text-xl font-semibold

/* H4 - Card titles */
.text-lg font-semibold
```

#### Body Text

```css
/* Large body text */
.text-lg

/* Standard body text */
/* Standard body text */
.text-base

/* Small text */
.text-sm

/* Extra small text */
.text-xs;
```

### Spacing Scale

#### Margins & Padding

```css
/* Section spacing */
.mb-8, .mt-8, .mb-12, .mt-12

/* Component spacing */
.mb-4, .mt-4, .mb-6, .mt-6

/* Card padding */
.p-4, .p-6, .p-8

/* Grid gaps */
.gap-4, .gap-6, .gap-8;
```

#### Layout Spacing

```css
/* Page sections */
.py-8, .py-12, .py-20

/* Component margins */
.mx-auto, .my-4, .my-8

/* Button padding */
.px-4 py-2, .px-6 py-3, .px-8 py-4;
```

## Components

### Button Component

The primary button component with multiple variants and sizes.

```tsx
import { Button } from '@/components/ui/Button';

// Primary button
<Button>Click me</Button>

// Secondary button
<Button variant="secondary">Secondary</Button>

// Ghost button
<Button variant="ghost">Ghost</Button>

// Danger button
<Button variant="danger">Delete</Button>

// Different sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
```

#### Button Variants

- `primary`: Blue background with white text
- `secondary`: Gray background with dark text
- `ghost`: Transparent with hover effects
- `danger`: Red background for destructive actions
- `success`: Green background for positive actions

#### Button Sizes

- `sm`: Height 32px, small padding
- `md`: Height 40px, standard padding
- `lg`: Height 48px, large padding

### Card Component

Flexible card component with multiple variants and sub-components.

```tsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';

// Basic card
<Card>
  <CardContent>Content here</CardContent>
</Card>

// Card with header
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>

// Elevated card
<Card variant="elevated">
  <CardContent>Elevated content</CardContent>
</Card>

// Ghost card
<Card variant="ghost">
  <CardContent>Ghost content</CardContent>
</Card>
```

#### Card Variants

- `standard`: Default white background with border
- `elevated`: Enhanced shadow for emphasis
- `ghost`: Subtle background for secondary content

#### Card Padding Options

- `none`: No padding
- `sm`: Small padding (16px)
- `md`: Medium padding (24px)
- `lg`: Large padding (32px)

### Input Component

Form input component with labels, error states, and icons.

```tsx
import { Input } from '@/components/ui/Input';

// Basic input
<Input placeholder="Enter text" />

// Input with label
<Input label="Email" type="email" />

// Input with error
<Input label="Password" type="password" error="Password is required" />

// Input with helper text
<Input label="Username" helperText="Choose a unique username" />

// Input with left icon
<Input
  label="Search"
  leftIcon={<Search className="h-4 w-4" />}
  placeholder="Search..."
/>
```

## Layout Patterns

### Page Structure

#### Standard Page Layout

```tsx
<div className="min-h-screen bg-gray-50 dark:bg-gray-900">
  {/* Page Banner */}
  <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 className="text-4xl md:text-5xl font-bold mb-4">Page Title</h1>
      <p className="text-xl opacity-90">Page description</p>
    </div>
  </div>

  {/* Main Content */}
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {/* Page Header */}
    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Section Title
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mt-1">
          Section description
        </p>
      </div>
    </div>

    {/* Content */}
    <div className="space-y-6">{/* Your content here */}</div>
  </div>
</div>
```

#### Card Grid Layout

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map((item) => (
    <Card key={item.id}>
      <CardContent className="p-4">{/* Card content */}</CardContent>
    </Card>
  ))}
</div>
```

#### List Layout

```tsx
<div className="space-y-6">
  {items.map((item) => (
    <Card key={item.id}>
      <CardContent className="p-6">{/* List item content */}</CardContent>
    </Card>
  ))}
</div>
```

### Form Layout

#### Search and Filter Bar

```tsx
<div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
  <div>
    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
      Section Title
    </h2>
    <p className="text-gray-600 dark:text-gray-300 mt-1">Found {count} items</p>
  </div>

  {/* Search Box */}
  <div className="relative max-w-md w-full">
    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
    <Input type="text" placeholder="Search..." className="pl-10 pr-4 py-3" />
  </div>
</div>
```

#### Filter Controls

```tsx
<div className="flex w-full items-center justify-between gap-6 flex-wrap">
  {/* Filter Button */}
  <div className="flex flex-col items-start w-full sm:w-auto">
    <Button
      variant="secondary"
      onClick={() => setShowFilters(!showFilters)}
      className="flex items-center gap-2 px-7 py-3 rounded-lg shadow-sm"
    >
      <Filter className="w-6 h-6" />
      <span>Show Filter</span>
      <ChevronDown
        className={`w-6 h-6 transition-transform ${
          showFilters ? "rotate-180" : ""
        }`}
      />
    </Button>

    {/* Filter Options */}
    {showFilters && (
      <div className="flex flex-wrap gap-3 mt-4 animate-fade-in w-full">
        {/* Filter pills */}
      </div>
    )}
  </div>

  {/* View Controls */}
  <div className="flex items-center gap-4 flex-shrink-0">
    {/* Sort dropdown and view toggle */}
  </div>
</div>
```

## Usage Examples

### Event Card Pattern

```tsx
<Card className="overflow-hidden">
  {/* Image */}
  <div className="relative h-48">
    <Image src={event.image} alt={event.title} fill className="object-cover" />

    {/* Badges */}
    <div className="absolute top-2 left-2 flex flex-col space-y-1">
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        {event.style}
      </span>
    </div>

    {/* Action Buttons */}
    <div className="absolute top-2 right-2 flex space-x-1">
      <Button variant="ghost" size="sm" onClick={handleFavorite}>
        <Heart className="h-4 w-4" />
      </Button>
    </div>
  </div>

  {/* Content */}
  <CardContent className="p-4">
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{event.title}</h3>
    <p className="text-gray-600 text-sm mb-3">{event.description}</p>
  </CardContent>
</Card>
```

### Form Pattern

```tsx
<Card className="p-6">
  <CardHeader>
    <CardTitle>Form Title</CardTitle>
  </CardHeader>

  <CardContent className="space-y-4">
    <Input label="Full Name" placeholder="Enter your full name" />

    <Input label="Email" type="email" placeholder="Enter your email" />

    <div className="flex gap-4">
      <Button variant="secondary">Cancel</Button>
      <Button>Submit</Button>
    </div>
  </CardContent>
</Card>
```

### Loading State Pattern

```tsx
<div className="animate-pulse">
  <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
  <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(6)].map((_, i) => (
      <Card key={i} className="p-6">
        <div className="h-48 bg-gray-200 rounded mb-4"></div>
        <div className="h-6 bg-gray-200 rounded mb-2"></div>
        <div className="h-4 bg-gray-200 rounded mb-4"></div>
        <div className="h-10 bg-gray-200 rounded"></div>
      </Card>
    ))}
  </div>
</div>
```

## Best Practices

### 1. Consistent Spacing

- Use the spacing scale: `mb-8`, `mt-16`, `gap-6`
- Maintain consistent margins between sections
- Use `space-y-4` or `space-y-6` for component spacing

### 2. Shadow Usage

- Default: `shadow-sm`
- Hover: `hover:shadow-md`
- Avoid: `shadow-lg`, `shadow-xl`, `shadow-2xl`

### 3. Border Consistency

- Use: `border border-gray-200`
- Avoid: arbitrary border colors or widths

### 4. Component Usage

- Always use `<Button>` instead of native `<button>`
- Always use `<Card>` for content containers
- Always use `<Input>` for form inputs

### 5. Typography Hierarchy

- Page titles: `text-4xl md:text-5xl font-bold`
- Section titles: `text-2xl font-bold`
- Subsection titles: `text-xl font-semibold`
- Card titles: `text-lg font-semibold`
- Body text: `text-base`
- Small text: `text-sm`

### 6. Color Usage

- Primary actions: `bg-blue-600 hover:bg-blue-700`
- Secondary actions: `bg-gray-100 hover:bg-gray-200`
- Success: `bg-green-600 hover:bg-green-700`
- Danger: `bg-red-600 hover:bg-red-700`
- Text: `text-gray-900` (primary), `text-gray-600` (secondary)

### 7. Responsive Design

- Use responsive prefixes: `md:`, `lg:`, `xl:`
- Mobile-first approach
- Consistent breakpoints across components

### 8. Accessibility

- Use semantic HTML elements
- Include proper ARIA labels
- Maintain sufficient color contrast
- Support keyboard navigation

## Implementation Notes

### Tailwind Configuration

The design system is built on top of Tailwind CSS with custom extensions:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          /* primary color scale */
        },
        secondary: {
          /* secondary color scale */
        },
        neutral: {
          /* neutral color scale */
        },
        success: "#22c55e",
        warning: "#f59e0b",
        error: "#ef4444",
        danger: "#ef4444",
        info: "#3b82f6",
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
      },
      screens: {
        xs: "475px",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
    },
  },
};
```

### Component Dependencies

- `class-variance-authority`: For component variants
- `clsx` + `tailwind-merge`: For class merging
- `lucide-react`: For consistent icon usage

### File Structure

```
components/ui/
├── Button.tsx      # Button component with variants
├── Card.tsx        # Card component with sub-components
├── Input.tsx       # Input component with states
└── SkeletonLoader.tsx  # Loading state component

lib/
└── utils.ts        # Utility functions (cn, etc.)
```

This design system ensures consistency, maintainability, and scalability across the entire Peykan Tourism application.
