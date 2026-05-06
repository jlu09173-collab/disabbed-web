# AbilityJobs - Static HTML Version

This folder contains standalone HTML files for the AbilityJobs platform. All pages are fully interconnected and can be opened directly in any web browser.

## Files Included

1. **index.html** - Homepage with hero section, benefits, and featured jobs
2. **login.html** - User login page
3. **register.html** - User registration page
4. **jobs.html** - Job listings page with search and filters
5. **employer-dashboard.html** - Employer dashboard with tabs for managing jobs and applications
6. **ngos.html** - NGO partners page with directory, benefits, and partnership application

## How to Use

### Option 1: Open Locally
1. Download all HTML files to a folder on your computer
2. Double-click any HTML file to open it in your default browser
3. Navigate between pages using the menu links

### Option 2: Host on a Server
1. Upload all HTML files to your web hosting service
2. Access the website through your domain
3. All navigation links will work seamlessly

### Render Django Web Service
Use this folder as the project root. Render can read `render.yaml` automatically.

Build command:
```bash
pip install -r requirements.txt
```

Start command:
```bash
gunicorn abilityjobs.wsgi:application
```

The Django app opens `index.html` at `/`, keeps every `.html` URL working, serves the logo and `app.js`, and redirects `job.html` to `jobs.html`.

## Features

✅ **Fully Responsive** - Works on desktop, tablet, and mobile devices
✅ **No Dependencies** - Uses Tailwind CSS CDN (no installation needed)
✅ **Interconnected Pages** - All navigation links work between pages
✅ **Modern Design** - Clean, accessible interface with AbilityJobs branding
✅ **Interactive Forms** - Functional forms with JavaScript validation
✅ **Accessibility First** - High contrast, clear fonts, and proper spacing

## Technology Stack

- HTML5
- Tailwind CSS (via CDN)
- Vanilla JavaScript
- Google Fonts (Poppins & Open Sans)

## Browser Compatibility

Works on all modern browsers:
- Chrome
- Firefox
- Safari
- Edge

## Notes

- Forms use JavaScript alerts for demonstration purposes
- No backend functionality is included (forms don't actually submit data)
- Images use placeholder backgrounds (can be replaced with actual images)
- All interactions are client-side only

## Customization

To customize the pages:
1. Open any HTML file in a text editor
2. Modify content, colors, or styles as needed
3. Save and refresh in your browser to see changes

## Support

For questions or support, contact: support@abilityjobs.com

---

© 2026 AbilityJobs - Inclusive Careers for Everyone
