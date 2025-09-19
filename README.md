<<<<<<< HEAD
# Universal Hierarchical Scraper

A powerful, zero-shot website structure detection and content extraction system. Built for universal compatibility with automatic platform detection and standardized output format.

## 🌟 Features

- **Zero-Shot Detection**: Automatically detects website structure without configuration
- **Platform Recognition**: Built-in detection for Substack, Medium, WordPress, Ghost, and more
- **Universal Output Format**: Standardized `{site, items[]}` JSON structure
- **Advanced Bot Evasion**: Popup dismissal, user-agent rotation, realistic headers and delays
- **Quality Content Extraction**: Proper markdown formatting with headers, paragraphs, and structure
- **Hierarchical Structure Analysis**: Intelligently discovers blog posts, articles, and content

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements_blog.txt
```

### Basic Usage

```bash
# Extract content with hierarchical detection
python hierarchical_scraper.py https://blog.example.com 10

# Extract from Substack blog
python hierarchical_scraper.py https://shreycation.substack.com 5
```

### Python Usage

```python
from hierarchical_scraper import HierarchicalScraper

# Create scraper instance
scraper = HierarchicalScraper()

# Extract content with universal format
results = scraper.scrape(url='https://blog.example.com', max_links=10)

# Process standardized results
print(f"Site: {results['site']}")
for item in results['items']:
    print(f"Title: {item['title']}")
    print(f"Content Type: {item['content_type']}")
    print(f"Source: {item['source_url']}")
    print(f"Content: {item['content'][:200]}...")
```

## 📖 Universal Output Format

Every scraper run produces the same standardized format:

```json
{
  "site": "https://shreycation.substack.com/archive",
  "items": [
    {
      "title": "Snacks: It's not too late for Euro Summer flights",
      "content": "# Snacks: It's not too late for Euro Summer flights\n\n### Procrastinators rejoice...",
      "content_type": "blog",
      "source_url": "https://shreycation.substack.com/p/snacks-its-not-too-late-for-euro"
    }
  ]
}
```

## 🔍 Platform Detection

Automatically detects and optimizes for:

- **Substack** (80-90% confidence detection)
- **Medium** (Platform-specific selectors)
- **WordPress** (Theme-agnostic extraction)
- **Ghost** (Modern blog platform)
- **Generic Blogs** (Universal fallback)

Detection includes confidence scoring and platform-specific optimizations.

## 🛡️ Bot Evasion Features

- **Popup Dismissal**: Automatically removes modals and overlays
- **User-Agent Rotation**: Random, realistic browser user agents  
- **Smart Headers**: Complete browser-like headers (Accept, DNT, Sec-Fetch-*)
- **Request Delays**: Intelligent delays between requests
- **Session Management**: Persistent sessions with proper referers
- **Alternative URLs**: Tries /archive and other patterns when main page fails

## 🎯 Content Quality

- **Proper Markdown**: Headers (#, ##), paragraphs, bold text (**)
- **Structure Preservation**: Maintains article hierarchy and formatting
- **Image Handling**: Includes images with proper markdown syntax
- **Clean Text**: Removes ads, navigation, and non-content elements

## 🔧 Configuration

The scraper automatically adapts but can be customized:

```python
# Platform detection settings
platform_info = scraper.platform_detector.detect_platform(soup, url)
print(f"Detected: {platform_info.platform} (confidence: {platform_info.confidence})")

# Content extraction settings  
content = scraper._extract_main_page_content(soup)  # Enhanced markdown
```

## 📁 Files

- `hierarchical_scraper.py` - Main universal scraper with zero-shot detection
- `requirements_blog.txt` - Required dependencies
- `universal_results_*.json` - Successful scraping results
- `README.md` - This documentation
- `LICENSE` - MIT License

## 🎯 Successful Test Results

### shreycation.substack.com
- ✅ Platform Detection: Substack (80% confidence)
- ✅ Successfully scraped 8 blog posts
- ✅ Proper markdown formatting with headers and structure
- ✅ Advanced bot evasion working (popup dismissal)
- ✅ Universal output format: `{site, items[]}`

### Content Quality Improvement
- ✅ **Before**: Wall of text without formatting
- ✅ **After**: Proper headers (27), paragraphs (62), bold text (6)
- ✅ **Structure**: 10,000 characters of well-formatted markdown content

## 🤝 Contributing

This scraper provides zero-shot capability. For enhancements:

1. Add new platform detection patterns
2. Improve content extraction quality  
3. Enhance bot evasion techniques
4. Expand universal output format

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Credits

- Built for reliable blog content extraction
- Focused on bot evasion and clean output
- Minimal dependencies for maximum reliability
=======
# OGTool
A web scraper that scrapes individual websites - part of a take away test.
>>>>>>> bf70b3e259f8da8d18e2b908bb6e4919035794f9
