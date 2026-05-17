# AutoShkolla Platform — UI Design Guidelines

**Version**: 1.0
**Last Updated**: March 9, 2026
**Status**: ACTIVE — Use for all frontend development

---

## Overview

This document provides comprehensive design direction for rebuilding the autoshkolla-platform driving school CRM with a modern, user-friendly interface. The redesign maintains all functionality and workflows from the legacy Bootstrap 3 system while dramatically improving usability, accessibility, and visual design.

**Key Goals**:
- Modernize from cramped, data-heavy Bootstrap 3 to clean, scannable interfaces
- Reduce cognitive load through information hierarchy and grouping
- Improve mobile/tablet support for field instructors
- Maintain Albanian language throughout with proper cultural adaptation
- Achieve WCAG AA accessibility standards

---

## 1. Design Philosophy

### Core Principles

1. **Information Hierarchy** — Show what matters first
   - Make the most common action the most prominent
   - Hide advanced options in collapsible sections
   - Use spacing and typography to guide attention

2. **Scanability** — Users should understand a page in 3 seconds
   - Logical grouping of related controls
   - Consistent patterns across pages
   - Visual indicators (colors, icons, badges) for status

3. **Albanian-First Design** — Full localization, not translation
   - All UI text in Albanian (Kosovo dialect)
   - Proper character support for ë, ç, ü, etc.
   - Date format: dd.MM.yyyy (Albanian standard)
   - Time format: HH:mm (24-hour)
   - Decimal separator: , (comma), not . (period)
   - Thousands separator: . (period), not , (comma)

4. **Progressive Disclosure** — Show complexity only when needed
   - Modal dialogs for confirmations (not full page navigations)
   - Expandable sections for advanced filters
   - Tooltips for explanation of complex fields
   - Wizard steps for multi-step processes

5. **Consistency** — Repeating patterns across the entire app
   - Same button styles for same actions everywhere
   - Same color meanings (green = success, red = danger)
   - Same spacing/margin rules throughout
   - Same component patterns for similar data types

6. **Performance** — Every interaction should feel snappy
   - Debounced searches (300ms)
   - Virtual scrolling for large tables (1000+ rows)
   - Lazy-load images and modals
   - Show loading states (spinners, skeletons) for async operations

---

## 2. Tech Stack & Component Library

### Core Technologies

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS (v3+) for utility-first styling
- **Component Library**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React (250+ icons)
- **Data Fetching**: React Query (TanStack Query v5)
- **State Management**: Zustand (global state)
- **Form Library**: React Hook Form + Zod validation
- **UI Patterns**: Custom components + shadcn/ui base

### Component Adoption Strategy

Use shadcn/ui for:
- Buttons, Input fields, Selects, Combobox
- Dropdowns, Popovers, Tooltips
- Dialogs, Sheets, Drawers
- Tables, Tabs, Accordion
- Cards, Badges, Progress bars
- Alerts, Toast notifications
- Forms, Checkboxes, Radio buttons, Switches

Build custom components for:
- DataTable (extended shadcn/ui Table with sorting, filtering, column visibility)
- Wizard/Stepper (multi-step forms)
- DateRangePicker (enhanced date picker)
- PageHeader (title + breadcrumbs + actions)
- DashboardGrid (responsive dashboard layout)

### Folder Structure

```
frontend/
├── components/
│   ├── ui/                    # shadcn/ui imported components
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   ├── candidates/            # Candidate-specific components
│   │   ├── CandidateDataTable.tsx
│   │   ├── CandidateForm.tsx
│   │   ├── CandidateDetailTabs.tsx
│   │   └── CandidateFilters.tsx
│   ├── payments/              # Payment module components
│   ├── reports/               # Reports/Evidence components
│   ├── common/                # Shared components (PageHeader, etc.)
│   └── dashboard/             # Dashboard components
├── lib/
│   ├── api.ts                 # Axios client with JWT interceptor
│   ├── api/
│   │   ├── candidates.ts      # Candidate API calls
│   │   ├── payments.ts        # Payment API calls
│   │   └── ...                # Other API modules
│   ├── schemas/               # Zod validation schemas
│   ├── hooks/                 # Custom hooks
│   └── utils.ts               # Helper functions
└── ...
```

---

## 3. Color Palette

### Primary Colors

| Color Name | Hex | Usage | Tailwind |
|---|---|---|---|
| **Blue 600** | `#2563EB` | Primary actions, links, active states | `blue-600` |
| **Blue 50** | `#EFF6FF` | Hover backgrounds, light accents | `blue-50` |
| **Slate 950** | `#0F172A` | Sidebar background, primary text | `slate-950` |
| **Slate 100** | `#F1F5F9` | Page background, table stripes | `slate-100` |

### Semantic Colors

| Color Name | Hex | Usage | Tailwind |
|---|---|---|---|
| **Success (Green)** | `#16A34A` | Paid, Active, Verified | `green-600` |
| **Success Light** | `#DCFCE7` | Success badge background | `green-100` |
| **Warning (Amber)** | `#D97706` | Pending, Unpaid, In Progress | `amber-600` |
| **Warning Light** | `#FEF3C7` | Warning badge background | `amber-100` |
| **Danger (Red)** | `#DC2626` | Error, Danger, Delete | `red-600` |
| **Danger Light** | `#FEE2E2` | Error badge background | `red-100` |
| **Info (Blue)** | `#0EA5E9` | Information, Notices | `sky-500` |
| **Info Light** | `#E0F2FE` | Info badge background | `sky-100` |

### Neutrals

| Color Name | Hex | Usage | Tailwind |
|---|---|---|---|
| **Slate 950** | `#0F172A` | Primary text, headings | `slate-950` |
| **Slate 700** | `#334155` | Secondary text, labels | `slate-700` |
| **Slate 500** | `#64748B` | Tertiary text, placeholders | `slate-500` |
| **Slate 300** | `#CBD5E1` | Borders, dividers | `slate-300` |
| **Slate 200** | `#E2E8F0` | Light borders, disabled state | `slate-200` |
| **White** | `#FFFFFF` | Card backgrounds, modals | `white` |

### Sidebar Variants

- **Dark Mode (Default)**: Background `#0F172A` (slate-950), text white, hover `#1E293B` (slate-800)
- **Light Mode (Optional)**: Background `#F8FAFC` (slate-50), text slate-950, hover `#E2E8F0` (slate-200)

### Usage Examples

```tsx
// Primary action button
<Button className="bg-blue-600 hover:bg-blue-700">Ruaj</Button>

// Success badge (paid)
<Badge className="bg-green-100 text-green-800">Paguar</Badge>

// Warning badge (pending)
<Badge className="bg-amber-100 text-amber-800">Në Pritje</Badge>

// Danger badge (unpaid)
<Badge className="bg-red-100 text-red-800">Pa Paguar</Badge>

// Primary text
<h1 className="text-slate-950 font-bold">Kandidatet</h1>

// Secondary text
<p className="text-slate-700">Lista e të gjithë kandidatëve</p>

// Tertiary text / placeholder
<p className="text-slate-500">Nuk ka rekorde për të shfaqur</p>
```

---

## 4. Typography

### Font Family

- **Primary Font**: Inter (or Segoe UI, system-ui as fallback)
- **Installation**: Use `next/font` to import from Google Fonts
- **Support**: Full support for Albanian characters (ë, ç, ü, ù, etc.)

```tsx
// In frontend/app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin', 'latin-ext'],
  variable: '--font-sans',
});
```

### Type Scale

Use Tailwind's default scale with these definitions:

| Size | Tailwind | px | Usage |
|---|---|---|---|
| **2XL** | `text-2xl` | 24px | Page main headings |
| **XL** | `text-xl` | 20px | Section headings |
| **LG** | `text-lg` | 18px | Subsection headings |
| **Base** | `text-base` | 16px | Body text, table cells |
| **SM** | `text-sm` | 14px | Form labels, help text |
| **XS** | `text-xs` | 12px | Secondary labels, captions |

### Line Height

- **Headings**: `leading-tight` (1.25)
- **Body**: `leading-relaxed` (1.625)
- **Form labels**: `leading-snug` (1.375)

### Font Weight

| Weight | Tailwind | Usage |
|---|---|---|
| 400 | `font-normal` | Body text, table cells |
| 500 | `font-medium` | Form labels, buttons (normal state) |
| 600 | `font-semibold` | Section headings, strong emphasis |
| 700 | `font-bold` | Page titles, important labels |

### Examples

```tsx
// Page title
<h1 className="text-2xl font-bold text-slate-950">
  Kandidatet
</h1>

// Section heading
<h2 className="text-lg font-semibold text-slate-700 mt-6 mb-4">
  Informatat Personale
</h2>

// Form label
<label className="text-sm font-medium text-slate-700">
  Emri Plotë
</label>

// Body text
<p className="text-base leading-relaxed text-slate-600">
  Ky është teksti i përshkrimit.
</p>

// Help text
<p className="text-xs text-slate-500 mt-1">
  Shënim: Këta të dhënat janë të detyrueshme.
</p>
```

### Albanian Character Support

Ensure the font includes:
- Lowercase: ë, ç, ü
- Uppercase: Ë, Ç, Ü
- Special: ù (in some names)
- Accents: é, è (in borrowed words)

Test strings:
- "Këtu janë të gjitha karakteret: ç, ë, ü, Ç, Ë, Ü"
- "Dita e Pavarësisë — 28 nëntor"

---

## 5. Layout Structure

### Main Application Shell

```tsx
// Layout hierarchy:
// └─ Header (fixed top)
//    ├─ Logo + App name
//    ├─ Breadcrumbs (on detail pages)
//    └─ User menu + notifications
// └─ Sidebar (fixed left or collapsible)
//    └─ Navigation groups + items
// └─ Main content area
//    ├─ Page title bar (if not in header)
//    └─ Page content
```

### Header Component

**Height**: 64px (Tailwind: h-16)

```tsx
<header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-40">
  {/* Left: Logo + Breadcrumbs */}
  <div className="flex items-center gap-8">
    <div className="flex items-center gap-2">
      <Logo className="w-8 h-8" />
      <span className="font-bold text-slate-950">AutoShkolla</span>
    </div>
    <Breadcrumbs /> {/* On detail pages only */}
  </div>

  {/* Right: User menu + Notifications */}
  <div className="flex items-center gap-4">
    <NotificationBell />
    <UserDropdown />
  </div>
</header>
```

### Sidebar Component

**Default Width**: 256px (Tailwind: w-64)
**Collapsed Width**: 80px (icon-only mode)
**Position**: Fixed left, starts below header

**Section Structure**:

```tsx
<aside className="fixed left-0 top-16 bottom-0 w-64 bg-slate-950 text-white overflow-y-auto transition-all duration-300">

  {/* School Selector (top) */}
  <div className="p-4 border-b border-slate-800">
    <Select>
      <option>AutoShkolla Prishtinë</option>
      <option>AutoShkolla Prizren</option>
    </Select>
  </div>

  {/* Navigation Groups */}
  <nav className="p-4 space-y-2">

    {/* Group: Modulet Kryesore */}
    <div>
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-2">
        Modulet Kryesore
      </p>
      <SidebarItem icon={Users} label="Kandidatet" href="/candidates" />
      <SidebarItem icon={BookOpen} label="Orët Teorike" href="/theory-hours" />
      <SidebarItem icon={Car} label="Orët Praktike" href="/practical-hours" />
    </div>

    {/* Group: Stafi */}
    <div className="mt-6">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-2">
        Stafi
      </p>
      <SidebarItem icon={Users} label="Instruktorë" href="/instructors" />
      <SidebarItem icon={BookOpen} label="Ligjerata" href="/lecturers" />
    </div>

    {/* ... more groups ... */}
  </nav>

  {/* Settings (bottom) */}
  <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800 space-y-1">
    <SidebarItem icon={Settings} label="Cilësimet" href="/settings" />
    <SidebarItem icon={LogOut} label="Dalje" onClick={logout} />
  </div>

</aside>
```

### Main Content Area

**Layout**: Sidebar (256px) + Content (flex-1) + padding

```tsx
<div className="flex h-screen">
  <Sidebar />
  <main className="flex-1 ml-64 mt-16 overflow-auto">
    <div className="p-8 max-w-7xl mx-auto">
      {/* Page content */}
      {children}
    </div>
  </main>
</div>
```

**Content Padding**: 32px (Tailwind: p-8) on desktop, 16px (p-4) on tablet
**Max Width**: 1280px (max-w-7xl) to prevent excessively wide content

### Sidebar Navigation Structure

Organize 16+ menu items into logical groups:

```
┌─ MODULET KRYESORE (Primary Modules)
│  ├─ Kandidatet
│  │  └─ (sub-items on list page, not in sidebar)
│  ├─ Orët Teorike
│  └─ Orët Praktike
│
├─ STAFI (Staff)
│  ├─ Instruktorë
│  └─ Ligjerata
│
├─ OPERACIONALE (Operational)
│  ├─ Automjetet
│  ├─ Pagesat
│  └─ Shpenzimet
│
├─ RAPORTET (Reports & Evidence)
│  ├─ Evidenca Oreve
│  ├─ Paraqitja e Testeve
│  └─ Vërtetimi
│
├─ ADMINISTRIMI (Administration)
│  ├─ Cilësimet e Shkollës
│  ├─ Kategoritë
│  ├─ Perdoruesit
│  └─ Rolet
│
└─ SISTEMI (System)
   ├─ Cilësimet
   ├─ Raportimet e Gabimeve
   └─ Dalje
```

**Total Items**: ~20 (reduced visual clutter compared to flat list)
**Hover State**: Background changes to slate-800, slight indent
**Active State**: Blue left border (4px), blue background highlight
**Icons**: 20px × 20px, Lucide React library

### Collapsed Sidebar Mode

When user clicks collapse button:
- Width reduces to 80px (Tailwind: w-20)
- Labels hidden, icons remain centered
- Tooltip appears on hover: `<Tooltip>{label}</Tooltip>`
- Smooth transition: `transition-all duration-300`

---

## 6. Data Tables (Core Component)

The Candidates List is the most-used page. Design it to be powerful yet intuitive.

### DataTable Component Structure

```tsx
<div className="space-y-4">
  {/* 1. Filter Bar */}
  <CandidateFilters
    onFilterChange={handleFilterChange}
    filters={activeFilters}
  />

  {/* 2. Active Filter Chips */}
  <div className="flex flex-wrap gap-2">
    {activeFilters.map(filter => (
      <FilterChip
        key={filter.id}
        label={filter.label}
        onRemove={() => removeFilter(filter.id)}
      />
    ))}
  </div>

  {/* 3. Table */}
  <CandidateDataTable
    data={candidates}
    columns={tableColumns}
    isLoading={isLoading}
    onSort={handleSort}
    onColumnVisibilityChange={handleColumnVisibility}
  />

  {/* 4. Pagination */}
  <Pagination
    currentPage={page}
    totalPages={totalPages}
    pageSize={pageSize}
    totalRecords={total}
    onPageChange={handlePageChange}
    onPageSizeChange={handlePageSizeChange}
  />
</div>
```

### Filter Bar Design

**Primary Layout**:
- 3–4 most-used filters visible: Category, Instructor, From Date, To Date
- "Kerko" (Search) input field, full width or spanning 2 columns
- "Filtrat e Avancuar" (Advanced Filters) toggle to expand additional options
- "Rezeto Filtrat" (Reset Filters) button

**Filter Bar HTML**:

```tsx
<div className="bg-white border border-slate-200 rounded-lg p-4 space-y-4">

  {/* Row 1: Main filters */}
  <div className="grid grid-cols-4 gap-4">
    <Select label="Kategoria" placeholder="Te gjitha">
      <option>Te gjitha</option>
      <option>A1</option>
      <option>A2</option>
      {/* ... */}
    </Select>

    <Select label="Instruktori" placeholder="Te gjitha">
      <option>Te gjitha</option>
      {instructors.map(i => <option key={i.id}>{i.name}</option>)}
    </Select>

    <DatePicker label="Nga Data" placeholder="dd.MM.yyyy" />
    <DatePicker label="Deri Data" placeholder="dd.MM.yyyy" />
  </div>

  {/* Row 2: Search + Advanced toggle */}
  <div className="flex gap-4 items-end">
    <Input
      label="Kerko Kandidatin"
      placeholder="Emri ose Nr. Personal"
      className="flex-1"
    />
    <Button
      variant="outline"
      onClick={() => setShowAdvanced(!showAdvanced)}
    >
      Filtrat e Avancuar {showAdvanced ? '▼' : '▶'}
    </Button>
    <Button
      variant="ghost"
      onClick={resetFilters}
    >
      Rezeto
    </Button>
  </div>

  {/* Row 3: Advanced filters (collapsed by default) */}
  {showAdvanced && (
    <div className="grid grid-cols-4 gap-4 pt-4 border-t border-slate-200">
      <Select label="Gjinia" placeholder="Te gjitha">
        <option>Te gjitha</option>
        <option>Mashkull</option>
        <option>Femër</option>
      </Select>
      <Select label="Stashi Pagese" placeholder="Te gjitha">
        <option>Te gjitha</option>
        <option>Paguar</option>
        <option>Pa Paguar</option>
      </Select>
      <Select label="Automatik" placeholder="Te gjitha">
        <option>Te gjitha</option>
        <option>Po</option>
        <option>Jo</option>
      </Select>
      <Select label="Ligjerues" placeholder="Te gjitha">
        <option>Te gjitha</option>
        {lecturers.map(l => <option key={l.id}>{l.name}</option>)}
      </Select>
    </div>
  )}

</div>
```

### Active Filter Chips

Show applied filters as removable chips above the table:

```tsx
<div className="flex flex-wrap gap-2">
  <FilterChip
    label="Kategoria: A2"
    onRemove={() => removeFilter('category')}
  />
  <FilterChip
    label="Instruktori: Agron Kelmendi"
    onRemove={() => removeFilter('instructor')}
  />
  <FilterChip
    label="Nga 01.01.2026"
    onRemove={() => removeFilter('dateFrom')}
  />
  {/* ... more chips ... */}
</div>
```

**FilterChip Component**:

```tsx
const FilterChip = ({ label, onRemove }) => (
  <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-full text-sm">
    <span className="text-slate-700">{label}</span>
    <button
      onClick={onRemove}
      className="text-slate-500 hover:text-slate-700 ml-1"
    >
      ✕
    </button>
  </div>
);
```

### Data Table Columns

**Default visible columns** (8–10):
1. **Checkbox** — for bulk actions
2. **#** — row number / ID
3. **Kandidati** — candidate name (clickable → detail page)
4. **Kategoria** — category badge (A1, A2, B, C, etc.)
5. **Nr. Personal** — ID number
6. **Telefoni** — phone number
7. **Instruktori** — instructor name
8. **Statusi i Pageses** — badge (Paguar/Pa Paguar/Pjeserisht)
9. **Orë Teorike** — theory hours (numeric, sortable)
10. **Aksione** — dropdown menu

**Hidden columns** (shown via column visibility toggle):
- Nr. Protokolit (Protocol number)
- Data Regjistrimit (Registration date)
- Ore Praktike (Practical hours)
- Ore Plotesuese (Supplementary hours)
- Çmimi (Price)
- Shuma Paguar (Amount paid)
- Borxhi (Debt)
- Testi Teorik (Theory test result)
- Testi Praktik (Practical test result)

### Table Features

**Column Headers**:
- Sortable columns show up/down arrows on hover
- Click to sort ascending; click again for descending
- Current sort indicator: arrow + bold weight

**Row Actions**:
- Right-most column: "Aksione" dropdown menu
- Actions: Shiko (View), Edito (Edit), Paguaj (Pay), Shtyp (Print), Fshi (Delete)

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="ghost" size="sm">
      Aksione ▼
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end">
    <DropdownMenuItem onClick={() => viewCandidate(row.id)}>
      Shiko
    </DropdownMenuItem>
    <DropdownMenuItem onClick={() => editCandidate(row.id)}>
      Edito
    </DropdownMenuItem>
    <DropdownMenuItem onClick={() => openPaymentDialog(row.id)}>
      Paguaj
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem onClick={() => printCandidate(row.id)}>
      Shtyp
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem
      onClick={() => deleteCandidate(row.id)}
      className="text-red-600"
    >
      Fshi
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

**Status Badges** (inside table cells):

```tsx
// Payment status
<Badge className="bg-green-100 text-green-800">Paguar</Badge>
<Badge className="bg-amber-100 text-amber-800">Pjeserisht Paguar</Badge>
<Badge className="bg-red-100 text-red-800">Pa Paguar</Badge>

// Candidate status
<Badge className="bg-blue-100 text-blue-800">Aktiv</Badge>
<Badge className="bg-slate-100 text-slate-800">Arkivuar</Badge>
<Badge className="bg-green-100 text-green-800">Përfunduar</Badge>

// Category
<Badge variant="outline">A1</Badge>
<Badge variant="outline">A2</Badge>
```

**Row Styling**:
- Hover: Very light gray background (`bg-slate-50`)
- Selected: Light blue background (`bg-blue-50`)
- Stripe (alternate rows): Subtle gray (`bg-slate-50` on even rows)

### Pagination Component

**Display Text** (at bottom left):
"Po shfaqen {from}-{to} nga {total} kandidatë"
Example: "Po shfaqen 1-10 nga 237 kandidatë"

**Rows Per Page** (dropdown, bottom left):
- Options: 10, 25, 50, 100
- Default: 10
- Label: "Rreshtat për faqe"

**Page Navigation** (bottom right):
- Previous/Next buttons
- Page numbers (1, 2, 3... with ellipsis if many pages)
- Current page highlighted in blue

```tsx
<div className="flex items-center justify-between py-4">
  {/* Left: Info + rows per page */}
  <div className="flex items-center gap-4">
    <p className="text-sm text-slate-600">
      Po shfaqen {startRow}-{endRow} nga {totalRecords} kandidatë
    </p>
    <Select
      value={pageSize}
      onChange={(e) => setPageSize(Number(e.target.value))}
      className="w-20"
    >
      <option value="10">10</option>
      <option value="25">25</option>
      <option value="50">50</option>
      <option value="100">100</option>
    </Select>
  </div>

  {/* Right: Page navigation */}
  <div className="flex items-center gap-2">
    <Button
      variant="outline"
      onClick={() => setPage(page - 1)}
      disabled={page === 1}
    >
      ← E Kaluara
    </Button>

    {pageNumbers.map(num => (
      <Button
        key={num}
        variant={num === page ? "default" : "outline"}
        onClick={() => setPage(num)}
        className={num === page ? "bg-blue-600" : ""}
      >
        {num}
      </Button>
    ))}

    <Button
      variant="outline"
      onClick={() => setPage(page + 1)}
      disabled={page === totalPages}
    >
      Tjetra →
    </Button>
  </div>
</div>
```

### Loading & Empty States

**Loading**:
- Show skeleton rows matching the column count
- 5–10 skeleton rows
- No pagination shown while loading

**Empty State**:
```tsx
<div className="flex flex-col items-center justify-center py-12 text-slate-500">
  <SearchIcon className="w-12 h-12 mb-4 text-slate-300" />
  <p className="text-lg font-medium text-slate-700">Nuk ka rezultate</p>
  <p className="text-sm">Nuk u gjet ndonjë kandidat që përputhet me kriteret tuaja.</p>
  <Button
    className="mt-4"
    onClick={resetFilters}
  >
    Rezeto Filtrat
  </Button>
</div>
```

---

## 7. Forms (Candidate Registration)

Candidate registration has 30+ fields. Use a wizard to avoid overwhelming users.

### Multi-Step Wizard

**Step Flow**:
1. **Personal Info** — Name, personal number, DOB, gender
2. **Contact & Address** — Phone, email, municipality, place
3. **Category & Training** — Category, instructor, vehicle, starting hours
4. **Documents & Medical** — Medical cert upload, ID copy upload, driver's license
5. **Payment** — Price, payment method, initial payment
6. **Review & Confirm** — Summary of all data, confirm to save

**Wizard Layout**:

```tsx
<div className="max-w-2xl mx-auto">
  {/* Progress indicator */}
  <div className="mb-8">
    <div className="flex justify-between mb-2">
      {[1, 2, 3, 4, 5, 6].map(num => (
        <div
          key={num}
          className={`flex items-center justify-center w-10 h-10 rounded-full font-bold text-sm ${
            num === currentStep
              ? 'bg-blue-600 text-white'
              : num < currentStep
              ? 'bg-green-600 text-white'
              : 'bg-slate-200 text-slate-600'
          }`}
        >
          {num < currentStep ? '✓' : num}
        </div>
      ))}
    </div>
    <div className="w-full h-1 bg-slate-200 rounded">
      <div
        className="h-1 bg-blue-600 rounded transition-all"
        style={{ width: `${((currentStep - 1) / 5) * 100}%` }}
      />
    </div>
  </div>

  {/* Step title */}
  <h2 className="text-2xl font-bold text-slate-950 mb-6">
    {stepTitles[currentStep]}
  </h2>

  {/* Form content for current step */}
  <Form step={currentStep} />

  {/* Navigation buttons */}
  <div className="flex justify-between mt-8">
    <Button
      variant="outline"
      onClick={previousStep}
      disabled={currentStep === 1}
    >
      ← E Kaluara
    </Button>

    {currentStep < 6 ? (
      <Button
        onClick={nextStep}
        disabled={!isStepValid}
      >
        Tjetra →
      </Button>
    ) : (
      <Button
        onClick={submitForm}
        className="bg-green-600"
      >
        Përfundo Regjistrimin
      </Button>
    )}
  </div>
</div>
```

### Step 1: Informatat Personale

```tsx
<div className="space-y-4">
  <Input
    label="Emri Plotë"
    placeholder="p.sh. Agron Kelmendi"
    required
    error={errors.fullName}
  />

  <Input
    label="Numri Personal (ID)"
    placeholder="p.sh. 03012980123"
    required
    error={errors.personalNumber}
    description="Numri i ID-s ose Pasaportës"
  />

  <DatePicker
    label="Data e Lindjes"
    placeholder="dd.MM.yyyy"
    required
    error={errors.dateOfBirth}
  />

  <Select
    label="Gjinia"
    required
    error={errors.gender}
  >
    <option value="">Zgjedh</option>
    <option value="M">Mashkull</option>
    <option value="F">Femër</option>
  </Select>
</div>
```

### Step 2: Kontakti & Adresa

```tsx
<div className="space-y-4">
  <Input
    label="Telefoni"
    placeholder="p.sh. +383 44 123 456"
    type="tel"
    required
    error={errors.phone}
  />

  <Input
    label="Email (Opsionale)"
    placeholder="kandidat@example.com"
    type="email"
    error={errors.email}
  />

  <Select
    label="Komuna"
    required
    error={errors.municipality}
  >
    <option value="">Zgjedh</option>
    {municipalities.map(m => (
      <option key={m.id} value={m.id}>{m.name}</option>
    ))}
  </Select>

  <Combobox
    label="Fshati/Vendbanimi"
    placeholder="Kerko fshatin..."
    options={places}
    required
    error={errors.place}
  />

  <Input
    label="Adresa (Opsionale)"
    placeholder="Rruga, numri, kompleksi"
    error={errors.address}
  />
</div>
```

### Step 3: Kategoria & Trajnimi

```tsx
<div className="space-y-4">
  <Select
    label="Kategoria"
    required
    error={errors.category}
  >
    <option value="">Zgjedh</option>
    <option value="A1">A1 (Motorçikla deri 125cc)</option>
    <option value="A2">A2 (Motorçikla deri 35kW)</option>
    <option value="B">B (Automjet)</option>
    <option value="BE">BE (Automjet + Rimorkio)</option>
    <option value="C">C (Kamion)</option>
    <option value="D">D (Autobus)</option>
  </Select>

  <Select
    label="Instruktori"
    required
    error={errors.instructorId}
  >
    <option value="">Zgjedh</option>
    {instructors.map(i => (
      <option key={i.id} value={i.id}>{i.name}</option>
    ))}
  </Select>

  <Select
    label="Automjeti"
    required
    error={errors.vehicleId}
  >
    <option value="">Zgjedh</option>
    {vehicles.map(v => (
      <option key={v.id} value={v.id}>{v.plate} - {v.model}</option>
    ))}
  </Select>

  <div className="grid grid-cols-2 gap-4">
    <Input
      label="Orët Teorike Fillestare"
      type="number"
      min="0"
      value={theoryHours}
      onChange={(e) => setTheoryHours(Number(e.target.value))}
      description="Sipas kategorisë: zakonisht 20-40 orë"
    />

    <Input
      label="Orët Praktike Fillestare"
      type="number"
      min="0"
      value={practicalHours}
      onChange={(e) => setPracticalHours(Number(e.target.value))}
      description="Sipas kategorisë: zakonisht 20-40 orë"
    />
  </div>
</div>
```

### Step 4: Dokumentet

```tsx
<div className="space-y-6">
  <div>
    <label className="text-sm font-medium text-slate-700 mb-2 block">
      Certifikata Mjekësore
    </label>
    <FileUpload
      accept=".pdf,.jpg,.jpeg,.png"
      maxSize={5}
      description="PDF, JPG ose PNG (max 5 MB)"
    />
  </div>

  <div>
    <label className="text-sm font-medium text-slate-700 mb-2 block">
      Fotokopia e ID-s / Pasaportës
    </label>
    <FileUpload
      accept=".pdf,.jpg,.jpeg,.png"
      maxSize={5}
      description="PDF, JPG ose PNG (max 5 MB)"
    />
  </div>

  <Checkbox
    label="Unë konfirmoj që të gjithë dokumentet janë të sakta"
    error={errors.documentsConfirmed}
  />
</div>
```

### Step 5: Pagesa

```tsx
<div className="space-y-4">
  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
    <p className="text-sm text-slate-600 mb-2">Çmimi i Trajnimit</p>
    <p className="text-3xl font-bold text-slate-950">
      {price.toLocaleString('sq-AL', {
        style: 'currency',
        currency: 'EUR'
      })}
    </p>
  </div>

  <Select
    label="Menyra e Pageses"
    required
    error={errors.paymentMethod}
  >
    <option value="">Zgjedh</option>
    <option value="cash">Para (Gotina)</option>
    <option value="bank_transfer">Transferimi Bancari</option>
    <option value="card">Karta e Kreditit/Debiti</option>
  </Select>

  <Input
    label="Shuma e Paguar Menjëherë"
    type="number"
    step="0.01"
    value={initialPayment}
    onChange={(e) => setInitialPayment(Number(e.target.value))}
    required
    error={errors.initialPayment}
  />

  <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-lg">
    <div>
      <p className="text-sm text-slate-600">Shuma e Paguar</p>
      <p className="text-lg font-bold text-slate-950">
        {initialPayment.toLocaleString('sq-AL', {
          style: 'currency',
          currency: 'EUR'
        })}
      </p>
    </div>
    <div>
      <p className="text-sm text-slate-600">Borxhi</p>
      <p className="text-lg font-bold text-red-600">
        {(price - initialPayment).toLocaleString('sq-AL', {
          style: 'currency',
          currency: 'EUR'
        })}
      </p>
    </div>
  </div>
</div>
```

### Step 6: Përmbledhje

```tsx
<div className="space-y-6">
  <Card>
    <CardHeader>
      <CardTitle>Informatat Personale</CardTitle>
    </CardHeader>
    <CardContent className="space-y-2">
      <div className="flex justify-between">
        <span className="text-slate-600">Emri:</span>
        <span className="font-medium">{formData.fullName}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-slate-600">Nr. Personal:</span>
        <span className="font-medium">{formData.personalNumber}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-slate-600">Data Lindjes:</span>
        <span className="font-medium">{formData.dateOfBirth}</span>
      </div>
      {/* ... more fields ... */}
    </CardContent>
  </Card>

  {/* Repeat for other steps */}

  <Checkbox
    label="Unë konfirmoj që të gjithë informatat janë të sakta dhe të plota"
    required
    error={errors.confirmationChecked}
  />

  <Alert className="bg-blue-50 border border-blue-200">
    <AlertIcon className="text-blue-600" />
    <AlertTitle>Përfundo Regjistrimin</AlertTitle>
    <AlertDescription>
      Pasi të konfirmosh, kandidati do të regjistrohet në sistem dhe do të mund të fillojë trajnimin.
    </AlertDescription>
  </Alert>
</div>
```

### Form Features

1. **Auto-save Draft** — Save form data to browser localStorage every 30 seconds
2. **Progress Persistence** — If user navigates away, resume from same step
3. **Inline Validation** — Show errors only after blur (not on every keystroke)
4. **Smart Defaults**:
   - Auto-fill theory/practical hours based on selected category
   - Pre-populate phone format mask
   - Auto-calculate debt when price changes
5. **Required Field Indicator** — Asterisk * in label, all required fields show error if empty when advancing

---

## 8. Candidate Detail Page

Instead of a cramped single page with 50 fields, use tabs.

### Tab Structure

```tsx
<div className="space-y-6">
  {/* Header with key metrics */}
  <CandidateHeader candidate={candidate} />

  {/* Tab navigation */}
  <Tabs defaultValue="overview">
    <TabsList className="w-full grid grid-cols-6">
      <TabsTrigger value="overview">Përmbledhja</TabsTrigger>
      <TabsTrigger value="theory-hours">Orët Teorike</TabsTrigger>
      <TabsTrigger value="practical-hours">Orët Praktike</TabsTrigger>
      <TabsTrigger value="payments">Pagesat</TabsTrigger>
      <TabsTrigger value="documents">Dokumentet</TabsTrigger>
      <TabsTrigger value="history">Historiku</TabsTrigger>
    </TabsList>

    {/* Tab 1: Overview */}
    <TabsContent value="overview">
      <CandidateOverviewTab candidate={candidate} />
    </TabsContent>

    {/* Tab 2: Theory Hours */}
    <TabsContent value="theory-hours">
      <TheoryHoursTab candidate={candidate} />
    </TabsContent>

    {/* ... other tabs ... */}
  </Tabs>
</div>
```

### CandidateHeader Component

```tsx
<div className="bg-white border border-slate-200 rounded-lg p-6">
  <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
    {/* Candidate info */}
    <div>
      <h1 className="text-2xl font-bold text-slate-950">
        {candidate.fullName}
      </h1>
      <p className="text-sm text-slate-600 mt-1">
        {candidate.personalNumber}
      </p>
    </div>

    {/* Status card */}
    <div className="text-right">
      <p className="text-xs text-slate-600 uppercase tracking-wide">Statusi</p>
      <Badge className="mt-2">
        {candidate.status === 'active' && 'Aktiv'}
        {candidate.status === 'archived' && 'Arkivuar'}
        {candidate.status === 'completed' && 'Përfunduar'}
      </Badge>
    </div>

    {/* Payment status */}
    <div className="text-right">
      <p className="text-xs text-slate-600 uppercase tracking-wide">Pagesa</p>
      <Badge className="mt-2">
        {candidate.paymentStatus === 'paid' && 'bg-green-100 text-green-800' || ''}
        {candidate.paymentStatus === 'unpaid' && 'bg-red-100 text-red-800' || ''}
        {candidate.paymentStatus === 'partial' && 'bg-amber-100 text-amber-800' || ''}
      </Badge>
    </div>

    {/* Progress */}
    <div>
      <p className="text-xs text-slate-600 uppercase tracking-wide mb-2">Përparimim</p>
      <Progress value={candidate.completionPercentage} />
      <p className="text-sm font-bold mt-1">{candidate.completionPercentage}%</p>
    </div>
  </div>

  {/* Action buttons */}
  <div className="flex gap-2 mt-6 border-t border-slate-200 pt-6">
    <Button onClick={editCandidate}>Edito Informatat</Button>
    <Button variant="outline" onClick={recordPayment}>Regjistro Pagese</Button>
    <Button variant="outline" onClick={printCandidate}>Shtyp</Button>
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost">Më Shumë ▼</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>Arkivoj</DropdownMenuItem>
        <DropdownMenuItem>Fshi</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</div>
```

### Tab 1: Përmbledhja (Overview)

```tsx
<div className="grid grid-cols-2 gap-6">
  {/* Personal Info Card */}
  <Card>
    <CardHeader>
      <CardTitle>Informatat Personale</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <DetailRow label="Emri Plotë" value={candidate.fullName} />
      <DetailRow label="Nr. Personal" value={candidate.personalNumber} />
      <DetailRow label="Data Lindjes" value={formatDate(candidate.dateOfBirth)} />
      <DetailRow label="Gjinia" value={candidate.gender === 'M' ? 'Mashkull' : 'Femër'} />
      <DetailRow label="Telefoni" value={candidate.phone} />
      <DetailRow label="Email" value={candidate.email} />
      <DetailRow label="Adresa" value={candidate.address} />
    </CardContent>
  </Card>

  {/* Training Info Card */}
  <Card>
    <CardHeader>
      <CardTitle>Informatat e Trajnimit</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <DetailRow label="Kategoria" value={candidate.category} />
      <DetailRow label="Instruktori" value={candidate.instructor.name} />
      <DetailRow label="Automjeti" value={`${candidate.vehicle.plate} - ${candidate.vehicle.model}`} />
      <DetailRow label="Data Regjistrimit" value={formatDate(candidate.createdAt)} />
      <DetailRow
        label="Orët Teorike Totale"
        value={`${candidate.theoryHoursDone} / ${candidate.theoryHoursRequired}`}
      />
      <DetailRow
        label="Orët Praktike Totale"
        value={`${candidate.practicalHoursDone} / ${candidate.practicalHoursRequired}`}
      />
    </CardContent>
  </Card>

  {/* Payment Summary Card */}
  <Card>
    <CardHeader>
      <CardTitle>Përmbledhja e Pageses</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-slate-600">Çmimi Total</span>
        <span className="font-bold text-slate-950">
          {formatCurrency(candidate.totalPrice)}
        </span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-slate-600">Shuma e Paguar</span>
        <span className="font-bold text-green-600">
          {formatCurrency(candidate.amountPaid)}
        </span>
      </div>
      <div className="border-t border-slate-200 pt-4 flex justify-between items-center">
        <span className="text-slate-600 font-medium">Borxhi</span>
        <span className="font-bold text-red-600 text-lg">
          {formatCurrency(candidate.debt)}
        </span>
      </div>
    </CardContent>
  </Card>

  {/* Recent Activity */}
  <Card>
    <CardHeader>
      <CardTitle>Aktiviteti Përkentesisht</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {candidate.recentActivity.map(activity => (
          <div key={activity.id} className="flex gap-3 text-sm">
            <span className="text-slate-500">{formatTime(activity.timestamp)}</span>
            <span className="text-slate-700">{activity.description}</span>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
</div>
```

### Tab 2: Orët Teorike (Theory Hours)

```tsx
<div className="space-y-6">
  {/* Summary stats */}
  <div className="grid grid-cols-3 gap-4">
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-slate-600 mb-2">Orët e Përfunduara</p>
        <p className="text-3xl font-bold text-slate-950">
          {candidate.theoryHoursDone}
        </p>
      </CardContent>
    </Card>
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-slate-600 mb-2">Orët e Kërkuara</p>
        <p className="text-3xl font-bold text-slate-950">
          {candidate.theoryHoursRequired}
        </p>
      </CardContent>
    </Card>
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-slate-600 mb-2">Përparimim</p>
        <Progress
          value={(candidate.theoryHoursDone / candidate.theoryHoursRequired) * 100}
        />
        <p className="text-sm font-bold mt-2">
          {Math.round((candidate.theoryHoursDone / candidate.theoryHoursRequired) * 100)}%
        </p>
      </CardContent>
    </Card>
  </div>

  {/* Theory sessions table */}
  <Card>
    <CardHeader className="flex justify-between items-center">
      <CardTitle>Sesionet e Orëve Teorike</CardTitle>
      <Button size="sm" onClick={openAddTheorySessionDialog}>
        + Shto Sesion
      </Button>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Tema</TableHead>
            <TableHead>Orë</TableHead>
            <TableHead>Ligjerues</TableHead>
            <TableHead>Aksione</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {candidate.theorySession.map(session => (
            <TableRow key={session.id}>
              <TableCell>{formatDate(session.date)}</TableCell>
              <TableCell>{session.topic}</TableCell>
              <TableCell>{session.hours}</TableCell>
              <TableCell>{session.lecturer.name}</TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">⋮</Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem>Edito</DropdownMenuItem>
                    <DropdownMenuItem>Fshi</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</div>
```

### Tab 3: Orët Praktike (Practical Hours)

Similar structure to Theory Hours:
- Summary cards (completed, required, progress)
- Practical sessions table with: Date, Time, Instructor, Vehicle, Route, Hours, Notes
- "Shto Sesion" button to record new practical session

### Tab 4: Pagesat (Payments)

```tsx
<div className="space-y-6">
  {/* Payment summary */}
  <Card>
    <CardContent className="pt-6">
      <div className="grid grid-cols-4 gap-4">
        <div>
          <p className="text-sm text-slate-600">Çmimi Total</p>
          <p className="text-2xl font-bold">{formatCurrency(candidate.totalPrice)}</p>
        </div>
        <div>
          <p className="text-sm text-slate-600">Paguar</p>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(candidate.amountPaid)}</p>
        </div>
        <div>
          <p className="text-sm text-slate-600">Borxhi</p>
          <p className="text-2xl font-bold text-red-600">{formatCurrency(candidate.debt)}</p>
        </div>
        <div className="text-right">
          <Button onClick={openPaymentDialog}>Regjistro Pagese</Button>
        </div>
      </div>
    </CardContent>
  </Card>

  {/* Payment history table */}
  <Card>
    <CardHeader>
      <CardTitle>Historiku i Pageseseve</CardTitle>
    </CardHeader>
    <CardContent>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Shuma</TableHead>
            <TableHead>Menyra</TableHead>
            <TableHead>Shënim</TableHead>
            <TableHead>Përgjegjës</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {candidate.payments.map(payment => (
            <TableRow key={payment.id}>
              <TableCell>{formatDate(payment.date)}</TableCell>
              <TableCell className="text-green-600 font-semibold">
                +{formatCurrency(payment.amount)}
              </TableCell>
              <TableCell>{payment.method}</TableCell>
              <TableCell>{payment.notes}</TableCell>
              <TableCell>{payment.recordedBy}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</div>
```

### Tab 5: Dokumentet (Documents)

```tsx
<div className="space-y-4">
  <div className="grid grid-cols-2 gap-4">
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Certifikata Mjekësore</CardTitle>
      </CardHeader>
      <CardContent>
        {candidate.medicalCertificate ? (
          <div className="flex items-center gap-2">
            <CheckCircle className="text-green-600" />
            <span className="text-sm">Ngarkuar {formatDate(candidate.medicalCertificateDate)}</span>
            <Button size="sm" variant="ghost" onClick={downloadFile}>Shkarko</Button>
          </div>
        ) : (
          <div className="text-slate-600 text-sm py-8 text-center">
            Nuk ka ngarkuar
          </div>
        )}
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle className="text-base">Fotokopia ID/Pasaporte</CardTitle>
      </CardHeader>
      <CardContent>
        {candidate.idCopy ? (
          <div className="flex items-center gap-2">
            <CheckCircle className="text-green-600" />
            <span className="text-sm">Ngarkuar {formatDate(candidate.idCopyDate)}</span>
            <Button size="sm" variant="ghost" onClick={downloadFile}>Shkarko</Button>
          </div>
        ) : (
          <div className="text-slate-600 text-sm py-8 text-center">
            Nuk ka ngarkuar
          </div>
        )}
      </CardContent>
    </Card>
  </div>

  {/* Print/Export section */}
  <Card>
    <CardHeader>
      <CardTitle>Dokumentet për Shtyp</CardTitle>
    </CardHeader>
    <CardContent className="space-y-2">
      <Button className="w-full justify-start" variant="outline" onClick={printCandidate}>
        <PrinterIcon className="w-4 h-4 mr-2" />
        Shtyp Letren e Kandidatit
      </Button>
      <Button className="w-full justify-start" variant="outline" onClick={printCertificate}>
        <FileIcon className="w-4 h-4 mr-2" />
        Shtyp Vërtetimin
      </Button>
      <Button className="w-full justify-start" variant="outline" onClick={exportPDF}>
        <DownloadIcon className="w-4 h-4 mr-2" />
        Eksporto PDF-në
      </Button>
    </CardContent>
  </Card>
</div>
```

### Tab 6: Historiku (History/Audit)

```tsx
<div className="space-y-4">
  <div className="space-y-3">
    {candidate.auditLog.map(entry => (
      <div key={entry.id} className="flex gap-4 pb-4 border-b border-slate-200 last:border-b-0">
        <div className="flex-shrink-0">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            {getAuditIcon(entry.action)}
          </div>
        </div>
        <div className="flex-1">
          <p className="font-medium text-slate-950">{entry.action}</p>
          <p className="text-sm text-slate-600">{entry.description}</p>
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>{entry.user}</span>
            <span>{formatDateTime(entry.timestamp)}</span>
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
```

---

## 9. Dashboard

The current system lacks a proper dashboard. Create one as the landing page after login.

### Dashboard Layout

```tsx
<div className="space-y-6">
  {/* Page header */}
  <PageHeader
    title="Tabela e Kontrollimit"
    subtitle="Përmbledhja e aktivitetit të sotës dhe ndekjes përfomative"
  />

  {/* Key metrics - 4 cards */}
  <div className="grid grid-cols-4 gap-4">
    <MetricCard
      title="Kandidatë Aktivë"
      value="24"
      change="+2 këtë muaj"
      icon={<Users />}
      color="blue"
    />
    <MetricCard
      title="Të Ardhurat këtë Muaj"
      value="€4,250"
      change="+€890 ndaj javës"
      icon={<TrendingUp />}
      color="green"
    />
    <MetricCard
      title="Pagesat në Pritje"
      value="€1,890"
      change="9 kandidatë"
      icon={<AlertCircle />}
      color="amber"
    />
    <MetricCard
      title="Seansët Sot"
      value="7"
      change="4 teorike, 3 praktike"
      icon={<Calendar />}
      color="purple"
    />
  </div>

  {/* Main content grid */}
  <div className="grid grid-cols-3 gap-6">

    {/* Left column - 2/3 width */}
    <div className="col-span-2 space-y-6">

      {/* Today's schedule */}
      <Card>
        <CardHeader>
          <CardTitle>Orari i Sotës</CardTitle>
        </CardHeader>
        <CardContent>
          <TodaysScheduleWidget />
        </CardContent>
      </Card>

      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle>Aktiviteti I Fundit</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentActivityFeed />
        </CardContent>
      </Card>

    </div>

    {/* Right column - 1/3 width */}
    <div className="space-y-6">

      {/* Candidate status breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Statusi i Kandidatëve</CardTitle>
        </CardHeader>
        <CardContent>
          <CandidateStatusChart />
        </CardContent>
      </Card>

      {/* Quick actions */}
      <Card>
        <CardHeader>
          <CardTitle>Aksione të Shpejta</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Button className="w-full" onClick={registerCandidate}>
            + Regjistroj Kandidat
          </Button>
          <Button className="w-full" variant="outline" onClick={recordPayment}>
            + Regjistro Pagese
          </Button>
          <Button className="w-full" variant="outline" onClick={recordSession}>
            + Regjistro Seansion
          </Button>
        </CardContent>
      </Card>

      {/* Upcoming events */}
      <Card>
        <CardHeader>
          <CardTitle>Eventeve Ardhshme</CardTitle>
        </CardHeader>
        <CardContent>
          <UpcomingEventsWidget />
        </CardContent>
      </Card>

    </div>

  </div>

</div>
```

### Metric Card Component

```tsx
const MetricCard = ({ title, value, change, icon, color }) => {
  const colorMap = {
    blue: 'bg-blue-50 border-blue-200 text-blue-600',
    green: 'bg-green-50 border-green-200 text-green-600',
    amber: 'bg-amber-50 border-amber-200 text-amber-600',
    purple: 'bg-purple-50 border-purple-200 text-purple-600',
  };

  return (
    <Card className={`border ${colorMap[color]}`}>
      <CardContent className="pt-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm text-slate-600 mb-1">{title}</p>
            <p className="text-3xl font-bold text-slate-950">{value}</p>
            <p className="text-xs text-slate-500 mt-2">{change}</p>
          </div>
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorMap[color].split(' ')[0]}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
```

### Today's Schedule Widget

```tsx
<div className="space-y-2">
  {todaysSchedule.map(session => (
    <div key={session.id} className="flex gap-3 p-3 bg-slate-50 rounded border border-slate-200">
      <div className="flex-shrink-0">
        <div className="w-12 h-12 bg-slate-200 rounded flex items-center justify-center font-bold text-slate-700">
          {session.time}
        </div>
      </div>
      <div className="flex-1">
        <p className="font-medium text-slate-950">{session.title}</p>
        <p className="text-sm text-slate-600">{session.instructor}</p>
      </div>
      <div className="text-right text-xs">
        <Badge variant="outline">{session.type === 'theory' ? 'Teorike' : 'Praktike'}</Badge>
      </div>
    </div>
  ))}
  {todaysSchedule.length === 0 && (
    <p className="text-slate-500 text-center py-8">Nuk ka seansione të planifikuara për sot</p>
  )}
</div>
```

### Recent Activity Feed

```tsx
<div className="space-y-3">
  {recentActivities.map(activity => (
    <div key={activity.id} className="flex gap-3 pb-3 border-b border-slate-200 last:border-b-0">
      <div className="flex-shrink-0">{getActivityIcon(activity.type)}</div>
      <div className="flex-1">
        <p className="text-sm font-medium text-slate-950">{activity.title}</p>
        <p className="text-xs text-slate-600">{activity.description}</p>
        <p className="text-xs text-slate-500 mt-1">{formatTimeAgo(activity.timestamp)}</p>
      </div>
    </div>
  ))}
</div>
```

---

### Admin Dashboard — Enhanced Features

Beyond the basic layout above, the admin dashboard should include:

**Revenue Chart (Recharts)**:
- Line chart showing monthly revenue for the last 6 months
- Target line overlay for comparison
- Hover tooltips with exact values in EUR
- Albanian month labels (Janar, Shkurt, Mars, Prill, Maj, Qershor, etc.)

**Candidates by Category (Donut Chart)**:
- Color-coded: B=blue, C=green, CE=amber, D=purple
- Center text showing total active candidates
- Legend with count and percentage

**Instructor Debt Summary Card**:
- Total outstanding debt from all instructors
- Top 3 instructors with highest debt
- Link to full instructor payments page

**Alerts Panel**:
```tsx
<Card className="border-amber-200 bg-amber-50">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <AlertTriangle className="h-5 w-5 text-amber-600" />
      Alarmet
    </CardTitle>
  </CardHeader>
  <CardContent className="space-y-3">
    {alerts.expiringRegistrations.map(alert => (
      <AlertItem
        icon={<Car />}
        text={`Regjistrimi i ${alert.plate} skadon për ${alert.days} ditë`}
        severity="warning"
      />
    ))}
    {alerts.overduePayments.map(alert => (
      <AlertItem
        icon={<CreditCard />}
        text={`${alert.candidate} ka borxh €${alert.amount} (${alert.days} ditë)`}
        severity="error"
      />
    ))}
  </CardContent>
</Card>
```

---

### 9b. Instructor Portal Dashboard

The instructor portal is a separate, simplified layout shown when a user with `role='instructor'` logs in.

**Instructor Portal Layout**:
```tsx
<div className="flex h-screen">
  {/* Simplified sidebar */}
  <InstructorSidebar />

  <main className="flex-1 overflow-auto bg-slate-50">
    {/* Header with instructor name and school name */}
    <InstructorHeader />

    {/* Dashboard content */}
    <div className="p-6 space-y-6">

      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-slate-950">
          Mirë se vjen, {instructor.first_name}!
        </h1>
        <p className="text-slate-500">
          Ja ku jeni sot — {format(new Date(), 'dd MMMM yyyy')}
        </p>
      </div>

      {/* Key metrics - 4 cards */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard title="Kandidatët e Mi" value="8" icon={<Users />} color="blue" />
        <MetricCard title="Mësimet Sot" value="3" icon={<Calendar />} color="green" />
        <MetricCard title="Borxhi Im" value="€260" icon={<CreditCard />} color="amber" />
        <MetricCard title="Mesazhe" value="2" icon={<MessageSquare />} color="purple" />
      </div>

      {/* Two columns */}
      <div className="grid grid-cols-2 gap-6">

        {/* This week's calendar */}
        <Card>
          <CardHeader>
            <CardTitle>Kalendari i Javës</CardTitle>
          </CardHeader>
          <CardContent>
            <WeeklyCalendarWidget lessons={weekLessons} />
          </CardContent>
        </Card>

        {/* My candidates quick view */}
        <Card>
          <CardHeader>
            <CardTitle>Kandidatët e Mi</CardTitle>
          </CardHeader>
          <CardContent>
            <CandidateQuickList candidates={myCandidates} />
          </CardContent>
        </Card>

      </div>

      {/* Debt overview */}
      <Card>
        <CardHeader>
          <CardTitle>Pagesat e Mia</CardTitle>
        </CardHeader>
        <CardContent>
          <InstructorDebtOverview
            totalOwed={780}
            totalPaid={520}
            balance={260}
            payments={recentPayments}
          />
        </CardContent>
      </Card>

    </div>
  </main>
</div>
```

**Instructor Sidebar Items**:
```tsx
const instructorNavItems = [
  { icon: <LayoutDashboard />, label: 'Paneli', href: '/instructor' },
  { icon: <Users />, label: 'Kandidatët e Mi', href: '/instructor/candidates' },
  { icon: <Calendar />, label: 'Kalendari', href: '/instructor/calendar' },
  { icon: <CreditCard />, label: 'Pagesat', href: '/instructor/payments' },
  { icon: <MessageSquare />, label: 'Mesazhet', href: '/instructor/messages' },
  { icon: <User />, label: 'Profili Im', href: '/instructor/profile' },
];
```

---

### 9c. Calendar / Scheduling UI

The calendar is used by both admins and instructors for scheduling practical lessons.

**Calendar Views**: Day, Week, Month (default: Week)

```tsx
<Card>
  <CardHeader className="flex flex-row items-center justify-between">
    <CardTitle>Kalendari</CardTitle>
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" onClick={prevWeek}>
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <span className="text-sm font-medium">{currentWeekLabel}</span>
      <Button variant="outline" size="sm" onClick={nextWeek}>
        <ChevronRight className="h-4 w-4" />
      </Button>
      <ToggleGroup type="single" value={view} onValueChange={setView}>
        <ToggleGroupItem value="day">Ditë</ToggleGroupItem>
        <ToggleGroupItem value="week">Javë</ToggleGroupItem>
        <ToggleGroupItem value="month">Muaj</ToggleGroupItem>
      </ToggleGroup>
    </div>
  </CardHeader>
  <CardContent>
    <CalendarGrid
      lessons={lessons}
      view={view}
      onLessonClick={openLessonDetail}
      onSlotClick={scheduleNewLesson}
    />
  </CardContent>
</Card>
```

**Lesson Color Coding**:
- Scheduled: `bg-blue-100 border-blue-300 text-blue-800`
- Completed: `bg-green-100 border-green-300 text-green-800`
- Cancelled: `bg-red-100 border-red-300 text-red-800`
- No-show: `bg-orange-100 border-orange-300 text-orange-800`

**Schedule Lesson Form**:
```tsx
<Dialog>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Planifiko Mësim Praktik</DialogTitle>
    </DialogHeader>
    <form className="space-y-4">
      <Select label="Kandidati" options={candidates} />
      <Select label="Instruktori" options={instructors} />
      <Select label="Automjeti" options={vehicles} />
      <DatePicker label="Data" />
      <div className="grid grid-cols-2 gap-4">
        <TimePicker label="Ora e Fillimit" />
        <TimePicker label="Ora e Mbarimit" />
      </div>
      <Textarea label="Shënime" />
      <DialogFooter>
        <Button variant="outline">Anulo</Button>
        <Button>Planifiko</Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

---

### 9d. Messaging UI

The messaging interface for instructor ↔ admin communication.

```tsx
<div className="grid grid-cols-3 h-[calc(100vh-200px)]">

  {/* Conversation list */}
  <div className="border-r border-slate-200 overflow-auto">
    <div className="p-4 border-b">
      <Button className="w-full" onClick={newConversation}>
        + Mesazh i Ri
      </Button>
    </div>
    {conversations.map(conv => (
      <div
        key={conv.id}
        className={cn(
          "p-4 border-b cursor-pointer hover:bg-slate-50",
          conv.unread_count > 0 && "bg-blue-50",
          selectedConv === conv.id && "bg-slate-100"
        )}
        onClick={() => selectConversation(conv.id)}
      >
        <div className="flex justify-between items-start">
          <p className="font-medium text-sm">{conv.subject}</p>
          {conv.unread_count > 0 && (
            <Badge className="bg-blue-600">{conv.unread_count}</Badge>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-1 truncate">{conv.last_message}</p>
        <p className="text-xs text-slate-400 mt-1">{formatRelativeTime(conv.last_message_at)}</p>
      </div>
    ))}
  </div>

  {/* Message thread */}
  <div className="col-span-2 flex flex-col">
    <div className="p-4 border-b bg-white">
      <h3 className="font-medium">{selectedConversation.subject}</h3>
      <p className="text-xs text-slate-500">
        {selectedConversation.participants.map(p => p.name).join(', ')}
      </p>
    </div>
    <div className="flex-1 overflow-auto p-4 space-y-4">
      {messages.map(msg => (
        <MessageBubble
          key={msg.id}
          message={msg}
          isOwn={msg.sender_id === currentUser.id}
        />
      ))}
    </div>
    <div className="p-4 border-t bg-white">
      <div className="flex gap-2">
        <Input
          placeholder="Shkruaj mesazh..."
          value={newMessage}
          onChange={e => setNewMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
        />
        <Button onClick={sendMessage}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  </div>

</div>
```

---

## 10. Print/PDF Integration

### Print Preview Dialog

Before printing/exporting PDF, show a preview:

```tsx
<Dialog open={showPrintPreview} onOpenChange={setShowPrintPreview}>
  <DialogContent className="max-w-4xl max-h-96">
    <DialogHeader>
      <DialogTitle>Shikimi Paraprak i Printimit</DialogTitle>
    </DialogHeader>

    <div className="border border-slate-200 rounded overflow-auto max-h-96">
      <div
        className="bg-white p-8"
        dangerouslySetInnerHTML={{ __html: previewHTML }}
      />
    </div>

    <DialogFooter>
      <Button
        variant="outline"
        onClick={() => setShowPrintPreview(false)}
      >
        Mbyll
      </Button>
      <Button
        onClick={handlePrint}
        className="bg-blue-600"
      >
        Shtyp
      </Button>
      <Button
        onClick={handleExportPDF}
        variant="outline"
      >
        Eksporto PDF
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Print Action Buttons

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">
      <PrinterIcon className="w-4 h-4 mr-2" />
      Shtyp
    </Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem onClick={printCandidateForm}>
      Formulari i Kandidatit
    </DropdownMenuItem>
    <DropdownMenuItem onClick={printCertificate}>
      Vërtestimi
    </DropdownMenuItem>
    <DropdownMenuItem onClick={printPaymentReceipt}>
      Fatura e Pageses
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem onClick={exportToPDF}>
      Eksporto si PDF
    </DropdownMenuItem>
    <DropdownMenuItem onClick={exportToExcel}>
      Eksporto si Excel
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### PDF Viewer

For viewing generated PDFs in-app:

```tsx
<Dialog open={showPDFViewer} onOpenChange={setShowPDFViewer}>
  <DialogContent className="max-w-4xl max-h-96">
    <DialogHeader>
      <DialogTitle>{pdfTitle}</DialogTitle>
    </DialogHeader>

    <embed
      src={pdfUrl}
      type="application/pdf"
      width="100%"
      height="500px"
    />

    <DialogFooter>
      <Button
        variant="outline"
        onClick={() => downloadPDF(pdfUrl)}
      >
        <DownloadIcon className="w-4 h-4 mr-2" />
        Shkarko
      </Button>
      <Button
        onClick={() => window.print()}
      >
        <PrinterIcon className="w-4 h-4 mr-2" />
        Shtyp
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

## 11. Responsive Design

### Breakpoints

Use Tailwind's responsive prefixes:
- **sm**: 640px — Tablets (landscape phones)
- **md**: 768px — Tablets (portrait)
- **lg**: 1024px — Small desktops
- **xl**: 1280px — Standard desktops
- **2xl**: 1536px — Large desktops

### Key Responsive Behaviors

**Sidebar**:
- Desktop (lg+): Fixed 256px width
- Tablet (md–lg): Collapsible to 80px icon-only mode
- Mobile (sm–md): Drawer/modal sidebar that overlays content

**Data Tables**:
- Desktop (lg+): Full table with all columns visible
- Tablet (md–lg): Hide low-priority columns, keep core data
- Mobile (sm–md): Stack as cards instead of table rows

**Grids**:
- Desktop (lg+): 4-column grid for metric cards
- Tablet (md–lg): 2-column grid
- Mobile (sm–md): Single column

**Examples**:

```tsx
{/* 4 columns desktop, 2 tablet, 1 mobile */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {metrics.map(m => <MetricCard key={m.id} {...m} />)}
</div>

{/* Hide on mobile */}
<div className="hidden md:block">
  {/* Content hidden on small screens */}
</div>

{/* Show only on mobile */}
<div className="md:hidden">
  {/* Mobile-specific layout */}
</div>

{/* Responsive spacing */}
<div className="p-4 md:p-6 lg:p-8">
  {/* More padding on larger screens */}
</div>
```

---

## 12. Accessibility (WCAG AA)

### ARIA Labels

All interactive elements must have descriptive labels:

```tsx
{/* Button with icon */}
<button aria-label="Fshi kandidatin">
  <TrashIcon className="w-4 h-4" />
</button>

{/* Form input */}
<input
  id="fullname"
  aria-label="Emri plotë i kandidatit"
  placeholder="p.sh. Agron Kelmendi"
/>

{/* Form select */}
<select
  aria-label="Zgjedh kategorinë e drejtimit"
  aria-describedby="category-hint"
>
  <option>Zgjedh</option>
  {/* ... */}
</select>
<p id="category-hint" className="text-xs text-slate-500">
  Kategoria përcakton orët dhe çmimin e trajnimit
</p>

{/* Icon-only tooltip */}
<Tooltip content="Shtyp për të printuar">
  <button aria-label="Shtyp këtë dokument">
    <PrinterIcon />
  </button>
</Tooltip>
```

### Keyboard Navigation

- All interactive elements must be keyboard focusable (tabindex >= 0)
- Tab order should match visual reading order (left-to-right, top-to-bottom)
- Focus indicators must be clearly visible (blue border or outline)
- Dialogs: Focus trap (Tab stays within modal)
- Dropdowns: Arrow keys navigate options, Enter to select

```tsx
// Example: Dialog with focus management
<Dialog open={open} onOpenChange={setOpen}>
  <DialogContent>
    <input
      autoFocus // Focus first field when dialog opens
      aria-label="Emri"
    />
    {/* ... more fields ... */}
    <button>Ruaj</button>
  </DialogContent>
</Dialog>
```

### Color Contrast

All text must meet WCAG AA contrast ratios:
- Body text (16px+): 4.5:1 contrast ratio
- Large text (18px+ bold or 24px+): 3:1 contrast ratio
- Normal text on colored backgrounds: Always test with tools like Contrast Checker

**Accessible Color Combinations**:
- White text on slate-950: ✓ 18:1
- Slate-950 text on white: ✓ 18:1
- Slate-700 text on white: ✓ 9:1
- Slate-600 text on white: ✓ 7:1
- Blue-600 text on white: ✓ 8:1
- Red-600 text on white: ✓ 5.5:1 (acceptable)

**Avoid**:
- Light gray on light background (low contrast)
- Red/green only to distinguish (color-blind unfriendly)
- Very small text (< 12px) for body content

### Screen Reader Support

- Use semantic HTML (buttons, links, headings)
- Labels for form inputs (not just placeholders)
- Table headers marked with `<th>`
- Lists use `<ul>` / `<ol>` / `<li>`
- Skip-to-content link at top of page

```tsx
{/* Skip link */}
<a href="#main-content" className="sr-only focus:not-sr-only">
  Kalo në përmbajtjen kryesore
</a>

{/* Semantic table */}
<table>
  <thead>
    <tr>
      <th scope="col">Emri</th>
      <th scope="col">Nr. Personal</th>
      <th scope="col">Kategoria</th>
    </tr>
  </thead>
  <tbody>
    {/* ... */}
  </tbody>
</table>

{/* Form with labels */}
<label htmlFor="email">Email</label>
<input
  id="email"
  type="email"
  aria-describedby="email-hint"
/>
<span id="email-hint" className="text-xs">Për komunikim zyrtar</span>
```

---

## 13. Albanian-Specific UI Patterns

### Common Button Labels

| Action | Albanian | Context |
|---|---|---|
| Search | Kerko | Filter bar, modal search |
| Register | Registro | Add new record |
| Save | Ruaj | Form submit |
| Close | Mbyll | Dialog, modal |
| Cancel | Anulo | Form abandon |
| Delete | Fshi | Destructive action (confirm first) |
| Edit | Edito | Open form for editing |
| Pay | Paguaj | Record payment |
| Print | Shtyp | Print to paper |
| Download | Shkarko | Download file |
| Upload | Ngarko | Upload file |
| Confirm | Konfirmo | Confirm action |
| Previous | ← E Kaluara | Wizard back button |
| Next | Tjetra → | Wizard forward button |

### Filter Labels

| Filter | Albanian |
|---|---|
| All | Te gjitha |
| Select | Zgjedh |
| From Date | Nga Data |
| To Date | Deri Data |
| Category | Kategoria |
| Status | Statusi |
| Payment Status | Statusi i Pageses |
| Paid | Paguar |
| Unpaid | Pa Paguar |
| Partially Paid | Pjeserisht Paguar |

### Status Badges

| Status | Albanian | Color | Usage |
|---|---|---|---|
| Active | Aktiv | Blue | Candidate enrolled, ongoing training |
| Archived | Arkivuar | Gray | Training completed or paused |
| Completed | Përfunduar | Green | All requirements met |
| Pending | Në Pritje | Amber | Awaiting action (payment, documents) |
| Approved | Miratuar | Green | Verified/confirmed |
| Rejected | Refuzuar | Red | Failed/denied |

### Table Labels

| Term | Albanian |
|---|---|
| Rows | Rreshtat |
| Page | Faqe |
| Next | Tjetra |
| Previous | E Kaluara |
| Showing X to Y of Z | Po shfaqen X deri Y prej Z rreshave |

### Date/Time Formatting

- **Date**: dd.MM.yyyy (e.g., 09.03.2026)
- **Time**: HH:mm (e.g., 14:30)
- **DateTime**: dd.MM.yyyy HH:mm
- **Date Range**: dd.MM.yyyy - dd.MM.yyyy
- **Months**: janar, shkurt, mars, prill, maj, qershor, korrik, gusht, shtator, tetor, nëntor, dhjetor
- **Days**: e hënë, e martë, e mërkurë, e enjte, e premte, e shtunë, e diel

### Number Formatting

- **Currency**: EUR or Eur symbol, decimal comma, thousands period
  - €1.234,56 (space before symbol optional)
  - 1.234,56 EUR
  - 1234,56 € (acceptable)
- **Decimal numbers**: Comma as separator (3,5 hours not 3.5)
- **Percentages**: 75,5% (not 75.5%)
- **Phone**: +383 44 123 456 (with spaces)

```tsx
// Format functions
const formatCurrency = (num, currency = 'EUR') => {
  return num.toLocaleString('sq-AL', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  });
};

const formatDate = (date) => {
  return date.toLocaleDateString('sq-AL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

const formatNumber = (num, fractionDigits = 2) => {
  return num.toLocaleString('sq-AL', {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
};
```

---

## 14. Component Examples

### Example 1: Candidates List Page

```tsx
// app/(dashboard)/candidates/page.tsx
'use client';

import { useState } from 'react';
import { CandidateFilters } from '@/components/candidates/CandidateFilters';
import { CandidateDataTable } from '@/components/candidates/CandidateDataTable';
import { FilterChip } from '@/components/common/FilterChip';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/common/PageHeader';
import { useCandidates } from '@/hooks/useCandidates';

export default function CandidatesPage() {
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortBy, setSortBy] = useState({ field: 'createdAt', direction: 'desc' });

  const { data, isLoading } = useCandidates({
    ...filters,
    page,
    pageSize,
    ...sortBy
  });

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page
  };

  const handleRemoveFilter = (filterKey) => {
    setFilters(prev => {
      const updated = { ...prev };
      delete updated[filterKey];
      return updated;
    });
  };

  const removeAllFilters = () => {
    setFilters({});
  };

  const activeFilterChips = Object.entries(filters).map(([key, value]) => ({
    id: key,
    label: `${key}: ${value}`,
  }));

  return (
    <main className="space-y-6">
      <PageHeader
        title="Kandidatet"
        subtitle="Administro të gjithë kandidatëve e sistemi i trajnimit"
        action={
          <Button onClick={() => router.push('/candidates/register')}>
            + Regjistroj Kandidat
          </Button>
        }
      />

      <CandidateFilters
        onFilterChange={handleFilterChange}
        onReset={removeAllFilters}
      />

      {activeFilterChips.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {activeFilterChips.map(chip => (
            <FilterChip
              key={chip.id}
              label={chip.label}
              onRemove={() => handleRemoveFilter(chip.id)}
            />
          ))}
        </div>
      )}

      <CandidateDataTable
        data={data?.records || []}
        totalRecords={data?.total || 0}
        currentPage={page}
        pageSize={pageSize}
        isLoading={isLoading}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
        onSort={setSortBy}
      />
    </main>
  );
}
```

### Example 2: Candidate Detail Page with Tabs

```tsx
// app/(dashboard)/candidates/[id]/page.tsx
'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CandidateHeader } from '@/components/candidates/CandidateHeader';
import { CandidateOverviewTab } from '@/components/candidates/tabs/OverviewTab';
import { TheoryHoursTab } from '@/components/candidates/tabs/TheoryHoursTab';
import { PracticalHoursTab } from '@/components/candidates/tabs/PracticalHoursTab';
import { PaymentsTab } from '@/components/candidates/tabs/PaymentsTab';
import { DocumentsTab } from '@/components/candidates/tabs/DocumentsTab';
import { HistoryTab } from '@/components/candidates/tabs/HistoryTab';
import { useCandidate } from '@/hooks/useCandidate';

export default function CandidateDetailPage({ params }) {
  const { candidate, isLoading } = useCandidate(params.id);

  if (isLoading) return <div>Po ngarkohet...</div>;
  if (!candidate) return <div>Kandidati nuk u gjet</div>;

  return (
    <main className="space-y-6">
      <CandidateHeader candidate={candidate} />

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="w-full grid grid-cols-6">
          <TabsTrigger value="overview">Përmbledhja</TabsTrigger>
          <TabsTrigger value="theory">Orët Teorike</TabsTrigger>
          <TabsTrigger value="practical">Orët Praktike</TabsTrigger>
          <TabsTrigger value="payments">Pagesat</TabsTrigger>
          <TabsTrigger value="documents">Dokumentet</TabsTrigger>
          <TabsTrigger value="history">Historiku</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <CandidateOverviewTab candidate={candidate} />
        </TabsContent>

        <TabsContent value="theory">
          <TheoryHoursTab candidate={candidate} />
        </TabsContent>

        <TabsContent value="practical">
          <PracticalHoursTab candidate={candidate} />
        </TabsContent>

        <TabsContent value="payments">
          <PaymentsTab candidate={candidate} />
        </TabsContent>

        <TabsContent value="documents">
          <DocumentsTab candidate={candidate} />
        </TabsContent>

        <TabsContent value="history">
          <HistoryTab candidate={candidate} />
        </TabsContent>
      </Tabs>
    </main>
  );
}
```

### Example 3: Candidate Registration Wizard

```tsx
// app/(dashboard)/candidates/register/page.tsx
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CandidateFormSchema } from '@/lib/schemas/candidate';
import { WizardStepper } from '@/components/common/WizardStepper';
import { PersonalInfoStep } from '@/components/candidates/wizard/PersonalInfoStep';
import { ContactAddressStep } from '@/components/candidates/wizard/ContactAddressStep';
import { CategoryTrainingStep } from '@/components/candidates/wizard/CategoryTrainingStep';
import { DocumentsStep } from '@/components/candidates/wizard/DocumentsStep';
import { PaymentStep } from '@/components/candidates/wizard/PaymentStep';
import { ReviewStep } from '@/components/candidates/wizard/ReviewStep';
import { Button } from '@/components/ui/button';

const STEPS = [
  { id: 1, title: 'Informatat Personale' },
  { id: 2, title: 'Kontakti & Adresa' },
  { id: 3, title: 'Kategoria & Trajnimi' },
  { id: 4, title: 'Dokumentet' },
  { id: 5, title: 'Pagesa' },
  { id: 6, title: 'Përmbledhja' },
];

export default function RegisterCandidatePage() {
  const [currentStep, setCurrentStep] = useState(1);
  const form = useForm({
    resolver: zodResolver(CandidateFormSchema),
    mode: 'onBlur',
  });

  const onSubmit = async (data) => {
    // Submit to API
    try {
      const response = await fetch('/api/v1/candidates', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      // Handle response
    } catch (error) {
      // Handle error
    }
  };

  const goToNextStep = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    } else {
      form.handleSubmit(onSubmit)();
    }
  };

  const goToPreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <main className="max-w-2xl mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Regjistro Kandidat</h1>

      <WizardStepper
        currentStep={currentStep}
        steps={STEPS}
        className="mb-8"
      />

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {currentStep === 1 && <PersonalInfoStep form={form} />}
        {currentStep === 2 && <ContactAddressStep form={form} />}
        {currentStep === 3 && <CategoryTrainingStep form={form} />}
        {currentStep === 4 && <DocumentsStep form={form} />}
        {currentStep === 5 && <PaymentStep form={form} />}
        {currentStep === 6 && <ReviewStep form={form} />}

        <div className="flex justify-between pt-8">
          <Button
            type="button"
            variant="outline"
            onClick={goToPreviousStep}
            disabled={currentStep === 1}
          >
            ← E Kaluara
          </Button>

          {currentStep < STEPS.length ? (
            <Button
              type="button"
              onClick={goToNextStep}
            >
              Tjetra →
            </Button>
          ) : (
            <Button
              type="submit"
              className="bg-green-600 hover:bg-green-700"
            >
              Përfundo Regjistrimin
            </Button>
          )}
        </div>
      </form>
    </main>
  );
}
```

---

## 15. Implementation Checklist

Use this checklist to track UI development:

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Tailwind CSS + shadcn/ui components
- [ ] Create color palette + typography system
- [ ] Build layout components: Header, Sidebar, MainLayout
- [ ] Create common components: Button, Input, Select, Card, Badge
- [ ] Set up dark mode support (optional for future)

### Phase 2: Core Pages (Weeks 3-4)
- [ ] Dashboard page with metric cards + widgets
- [ ] Candidates list with filters + data table
- [ ] Candidate registration wizard (6 steps)
- [ ] Candidate detail page with tabs
- [ ] Instructor/Lecturer list pages

### Phase 3: Supporting Pages (Weeks 5-6)
- [ ] Payments page + payment form
- [ ] Theory hours page
- [ ] Practical hours page
- [ ] Vehicles management
- [ ] Reports/Evidence pages

### Phase 4: Polish & Accessibility (Weeks 7-8)
- [ ] Add loading states + skeletons
- [ ] Add error boundaries + error pages
- [ ] Test keyboard navigation
- [ ] Test screen readers
- [ ] Test on tablet/mobile
- [ ] Finalize print/PDF styles
- [ ] Performance optimization

---

## Reference: Component Import Patterns

All components should follow this pattern:

```tsx
// ✓ GOOD: Centralized imports from shadcn/ui
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// ✗ BAD: Inline styles, direct HTML elements
<button style={{ backgroundColor: '#2563EB' }}>Click me</button>

// ✓ GOOD: Using custom hooks for data fetching
const { data, isLoading, error } = useCandidates();

// ✗ BAD: useState + useEffect fetch pattern
const [candidates, setCandidates] = useState([]);
useEffect(() => {
  fetch('/api/candidates').then(r => r.json()).then(setCandidates);
}, []);
```

---

## Summary

This design system provides:

1. **Modern, clean aesthetic** — Move away from cramped Bootstrap 3 tables
2. **Information hierarchy** — Guide users to primary actions
3. **Accessibility** — WCAG AA compliant, keyboard navigable, screen reader friendly
4. **Albanian-first** — Full localization with proper character support and cultural patterns
5. **Responsive design** — Works on desktop, tablet, and mobile
6. **Component reusability** — shadcn/ui + custom components for rapid development
7. **Consistent patterns** — Repeating elements across the entire app

**Start building** by following the implementation checklist in phase order. Refer back to this document for component patterns and design decisions.

For questions on specific components or patterns, update this document with new examples as you discover them.

---

**Document Version History**:
- **v1.0** (Mar 9, 2026) — Initial comprehensive design guidelines
