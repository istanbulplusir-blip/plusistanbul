# Component Usage Guide - Peykan Tourism

This guide provides practical examples and best practices for using the design system components in your application.

## Quick Start

### Import Components

```tsx
import { Button } from "@/components/ui/Button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
```

### Basic Usage

```tsx
// Simple button
<Button>Click me</Button>

// Card with content
<Card>
  <CardContent>Hello World</CardContent>
</Card>

// Input field
<Input placeholder="Enter text" />
```

## Button Component

### Variants

```tsx
// Primary (default)
<Button>Primary Action</Button>

// Secondary
<Button variant="secondary">Secondary Action</Button>

// Ghost
<Button variant="ghost">Subtle Action</Button>

// Danger
<Button variant="danger">Delete</Button>

// Success
<Button variant="success">Save</Button>
```

### Sizes

```tsx
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
```

### With Icons

```tsx
import { Plus, Trash2, Save } from 'lucide-react';

<Button>
  <Plus className="w-4 h-4 mr-2" />
  Add Item
</Button>

<Button variant="danger">
  <Trash2 className="w-4 h-4 mr-2" />
  Delete
</Button>

<Button variant="success">
  <Save className="w-4 h-4 mr-2" />
  Save Changes
</Button>
```

### Button Groups

```tsx
<div className="flex gap-2">
  <Button variant="secondary">Cancel</Button>
  <Button>Submit</Button>
</div>

<div className="flex gap-2">
  <Button size="sm" variant="ghost">Edit</Button>
  <Button size="sm" variant="ghost">View</Button>
  <Button size="sm" variant="danger">Delete</Button>
</div>
```

## Card Component

### Basic Card

```tsx
<Card>
  <CardContent className="p-6">
    <p>Simple card content</p>
  </CardContent>
</Card>
```

### Card with Header

```tsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
</Card>
```

### Card with Footer

```tsx
<Card>
  <CardContent>
    <p>Card content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Card Variants

```tsx
// Standard (default)
<Card>
  <CardContent>Standard card</CardContent>
</Card>

// Elevated
<Card variant="elevated">
  <CardContent>Elevated card with more shadow</CardContent>
</Card>

// Ghost
<Card variant="ghost">
  <CardContent>Ghost card with subtle background</CardContent>
</Card>
```

### Card Padding Options

```tsx
<Card padding="none">
  <CardContent>No padding</CardContent>
</Card>

<Card padding="sm">
  <CardContent>Small padding (16px)</CardContent>
</Card>

<Card padding="md">
  <CardContent>Medium padding (24px)</CardContent>
</Card>

<Card padding="lg">
  <CardContent>Large padding (32px)</CardContent>
</Card>
```

### Complex Card Layout

```tsx
<Card>
  <CardHeader>
    <div className="flex items-center justify-between">
      <CardTitle>User Profile</CardTitle>
      <Button variant="ghost" size="sm">
        <Edit className="w-4 h-4 mr-2" />
        Edit
      </Button>
    </div>
  </CardHeader>
  <CardContent className="space-y-4">
    <div className="grid grid-cols-2 gap-4">
      <Input label="First Name" placeholder="John" />
      <Input label="Last Name" placeholder="Doe" />
    </div>
    <Input label="Email" type="email" placeholder="john@example.com" />
  </CardContent>
  <CardFooter>
    <div className="flex gap-2 w-full">
      <Button variant="secondary" className="flex-1">
        Cancel
      </Button>
      <Button className="flex-1">Save Changes</Button>
    </div>
  </CardFooter>
</Card>
```

## Input Component

### Basic Input

```tsx
<Input placeholder="Enter text" />
```

### Input with Label

```tsx
<Input label="Email Address" type="email" placeholder="Enter your email" />
```

### Input with Error

```tsx
<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>
```

### Input with Helper Text

```tsx
<Input
  label="Username"
  helperText="Choose a unique username between 3-20 characters"
/>
```

### Input with Icons

```tsx
import { Search, Mail, Lock } from 'lucide-react';

<Input
  label="Search"
  leftIcon={<Search className="w-4 w-4" />}
  placeholder="Search..."
/>

<Input
  label="Email"
  leftIcon={<Mail className="w-4 w-4" />}
  type="email"
  placeholder="Enter email"
/>

<Input
  label="Password"
  leftIcon={<Lock className="w-4 w-4" />}
  rightIcon={<Eye className="w-4 w-4" />}
  type="password"
/>
```

### Input Types

```tsx
// Text
<Input label="Name" placeholder="Enter name" />

// Email
<Input label="Email" type="email" placeholder="Enter email" />

// Password
<Input label="Password" type="password" />

// Number
<Input label="Age" type="number" min="0" max="120" />

// Date
<Input label="Birth Date" type="date" />

// Time
<Input label="Meeting Time" type="time" />

// URL
<Input label="Website" type="url" placeholder="https://example.com" />

// Tel
<Input label="Phone" type="tel" placeholder="+1 (555) 123-4567" />
```

## Layout Patterns

### Page Header

```tsx
<div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
  <div>
    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
      Page Title
    </h2>
    <p className="text-gray-600 dark:text-gray-300 mt-1">
      Page description or summary
    </p>
  </div>

  <div className="flex gap-2">
    <Button variant="secondary">Secondary Action</Button>
    <Button>Primary Action</Button>
  </div>
</div>
```

### Search and Filter Bar

```tsx
<div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
  <div>
    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
      Products
    </h2>
    <p className="text-gray-600 dark:text-gray-300 mt-1">
      Found {count} products
    </p>
  </div>

  <div className="flex gap-4">
    <div className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
      <Input placeholder="Search products..." className="pl-10 w-64" />
    </div>

    <Button variant="secondary">
      <Filter className="w-4 h-4 mr-2" />
      Filters
    </Button>
  </div>
</div>
```

### Grid Layout

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map((item) => (
    <Card key={item.id}>
      <CardContent className="p-4">
        <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
        <p className="text-gray-600 text-sm mb-4">{item.description}</p>
        <Button className="w-full">View Details</Button>
      </CardContent>
    </Card>
  ))}
</div>
```

### List Layout

```tsx
<div className="space-y-4">
  {items.map((item) => (
    <Card key={item.id}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">{item.title}</h3>
            <p className="text-gray-600 text-sm">{item.description}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm">
              Edit
            </Button>
            <Button variant="ghost" size="sm">
              View
            </Button>
            <Button variant="danger" size="sm">
              Delete
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  ))}
</div>
```

### Form Layout

```tsx
<Card className="max-w-2xl mx-auto">
  <CardHeader>
    <CardTitle>Contact Form</CardTitle>
  </CardHeader>

  <CardContent className="space-y-4">
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Input label="First Name" placeholder="Enter first name" required />
      <Input label="Last Name" placeholder="Enter last name" required />
    </div>

    <Input label="Email" type="email" placeholder="Enter email" required />
    <Input label="Phone" type="tel" placeholder="Enter phone number" />

    <Input
      label="Message"
      placeholder="Enter your message"
      helperText="Tell us how we can help you"
    />
  </CardContent>

  <CardFooter>
    <div className="flex gap-2 w-full">
      <Button variant="secondary" className="flex-1">
        Cancel
      </Button>
      <Button className="flex-1">Send Message</Button>
    </div>
  </CardFooter>
</Card>
```

### Loading States

```tsx
// Skeleton loading
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

// Button loading state
<Button disabled>
  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
  Loading...
</Button>
```

## Best Practices

### 1. Consistent Spacing

```tsx
// ✅ Good - Use consistent spacing
<div className="space-y-4">
  <Card>
    <CardContent className="p-6">
      <h3 className="text-lg font-semibold mb-2">Title</h3>
      <p className="text-gray-600 mb-4">Description</p>
      <Button>Action</Button>
    </CardContent>
  </Card>
</div>

// ❌ Bad - Inconsistent spacing
<div>
  <Card>
    <CardContent className="p-4">
      <h3 className="text-lg font-semibold mb-3">Title</h3>
      <p className="text-gray-600 mb-6">Description</p>
      <Button>Action</Button>
    </CardContent>
  </Card>
</div>
```

### 2. Proper Component Usage

```tsx
// ✅ Good - Use design system components
<Button variant="primary" size="md">Click me</Button>
<Card variant="standard" padding="md">
  <CardContent>Content</CardContent>
</Card>

// ❌ Bad - Don't use native elements
<button className="bg-blue-600 text-white px-4 py-2 rounded">Click me</button>
<div className="bg-white border rounded shadow">Content</div>
```

### 3. Responsive Design

```tsx
// ✅ Good - Mobile-first approach
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
  {/* Content */}
</div>

// ✅ Good - Responsive text sizes
<h1 className="text-3xl md:text-4xl lg:text-5xl font-bold">Title</h1>

// ✅ Good - Responsive spacing
<div className="p-4 md:p-6 lg:p-8">Content</div>
```

### 4. Accessibility

```tsx
// ✅ Good - Proper labels and ARIA
<Input
  label="Email Address"
  aria-describedby="email-help"
  required
/>
<div id="email-help" className="text-sm text-gray-500">
  We'll never share your email with anyone else.
</div>

// ✅ Good - Semantic button usage
<Button onClick={handleSubmit} type="submit">
  Submit Form
</Button>
```

### 5. Performance

```tsx
// ✅ Good - Memoize expensive components
const MemoizedCard = React.memo(Card);

// ✅ Good - Use proper keys in lists
{
  items.map((item) => (
    <Card key={item.id}>
      <CardContent>{item.content}</CardContent>
    </Card>
  ));
}

// ✅ Good - Lazy load when possible
const LazyComponent = React.lazy(() => import("./LazyComponent"));
```

## Common Patterns

### Modal Pattern

```tsx
<Card className="max-w-md mx-auto">
  <CardHeader>
    <CardTitle>Confirm Action</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Are you sure you want to proceed?</p>
  </CardContent>
  <CardFooter>
    <div className="flex gap-2 w-full">
      <Button variant="secondary" className="flex-1">
        Cancel
      </Button>
      <Button variant="danger" className="flex-1">
        Confirm
      </Button>
    </div>
  </CardFooter>
</Card>
```

### Alert Pattern

```tsx
<Card className="border-l-4 border-l-red-500">
  <CardContent className="p-4">
    <div className="flex items-center">
      <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
      <div>
        <h4 className="font-semibold text-red-800">Error</h4>
        <p className="text-red-600 text-sm">
          Something went wrong. Please try again.
        </p>
      </div>
    </div>
  </CardContent>
</Card>
```

### Success Pattern

```tsx
<Card className="border-l-4 border-l-green-500">
  <CardContent className="p-4">
    <div className="flex items-center">
      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
      <div>
        <h4 className="font-semibold text-green-800">Success</h4>
        <p className="text-green-600 text-sm">
          Your changes have been saved successfully.
        </p>
      </div>
    </div>
  </CardContent>
</Card>
```

This guide covers the most common use cases for the design system components. For more advanced patterns and customization options, refer to the main DESIGN_SYSTEM.md documentation.
