# Frontend Design Skill

Frontend development and design patterns for modern web applications.

## Features

### 1. Design System Generator
- Component architecture templates
- Theme configuration
- Color palette generation
- Typography guidelines

### 2. Code Patterns
- State management patterns (React, Vue, Svelte)
- Component composition techniques
- Performance optimization strategies
- Accessibility best practices

### 3. CSS & Styling
- Modern CSS techniques (Grid, Flexbox, CSS-in-JS)
- Responsive design patterns
- Animation and transitions
- CSS architecture (BEM, ITCSS)

### 4. Best Practices
- Code organization
- Testing strategies
- Debugging techniques
- Performance monitoring

## Usage

### Commands

```
/frontend design-system    # Generate design system template
/frontend component       # Create component boilerplate
/frontend css-pattern     # Get CSS pattern examples
/frontend review          # Review frontend code quality
```

### Examples

**Generate a React component:**
```
/frontend component --framework react --type button
```

**Get responsive design tips:**
```
/frontend css-pattern responsive
```

## Supported Frameworks
- React
- Vue.js
- Svelte
- Angular
- Solid.js

## Resources
- Component library recommendations
- Tooling setup guides
- Performance checklists
- Accessibility audit tools

## Quick Reference

### CSS Grid Layout
```css
.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}
```

### Responsive Breakpoints
```css
@media (max-width: 768px) { /* Mobile */ }
@media (min-width: 769px) and (max-width: 1024px) { /* Tablet */ }
@media (min-width: 1025px) { /* Desktop */ }
```

### React Component Structure
```jsx
const Component = ({ prop }) => {
  const [state, setState] = useState(null);
  
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  return <div>{/* Content */}</div>;
};
```

## Version
1.0.0

## Author
Frontend Design Team