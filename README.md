<<<<<<< HEAD
# Universal Hierarchical Scraper

A powerful, zero-shot website structure detection and content extraction system. Built for universal compatibility with automatic platform detection and standardized output format.

## 🌟 Features

- **Zero-Shot Detection**: Automatically detects website structure without configuration
- **Platform Recognition**: Built-in detection for Substack, Medium, WordPress, Ghost, and more
- **Universal Output Format**: Standardized `{site, items[]}` JSON structure
- **Advanced Bot Evasion**: Popup dismissal, user-agent rotation, realistic headers and delays
- **Quality Content Extraction**: Full blog article content (not just summaries)
- **Hierarchical Structure Analysis**: Intelligently discovers blog posts, articles, and content

## 🚀 Quick Start Guide

### Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/Mario263/OGTool.git
cd OGTool

# Install dependencies
pip install -r requirements_blog.txt
```

### Step 2: Basic Command Line Usage

The scraper uses this simple command format:
```bash
python hierarchical_scraper.py <URL> <max_additional_pages> <max_articles>
```

**Parameters:**
- `<URL>` - The website URL to scrape
- `<max_additional_pages>` - Number of additional pages to crawl (default: 0)
- `<max_articles>` - Maximum number of articles to extract (default: 20)

### Step 3: Examples

```bash
# Extract 5 articles from a blog
python hierarchical_scraper.py "https://nilmamano.com/blog/category/dsa" 0 5

# Extract 10 articles from Substack
python hierarchical_scraper.py "https://shreycation.substack.com" 0 10

# Extract from TechCrunch (3 articles)
python hierarchical_scraper.py "https://techcrunch.com" 0 3

# Extract from Stripe blog (5 articles)
python hierarchical_scraper.py "https://blog.stripe.com" 0 5
```

### Step 4: Understanding the Output

The scraper saves results in JSON format with filename pattern:
```
universal_results_<domain>_<timestamp>.json
```

**Output Structure:**
```json
{
  "site": "https://example.com",
  "items": [
    {
      "title": "Article Title",
      "content": "Full article content in markdown format...",
      "content_type": "blog",
      "source_url": "https://example.com/article-url"
    }
  ]
}
```

## 📖 Detailed Usage Instructions

### For Blog Content Extraction
```bash
# For DSA blog articles (get full content)
python hierarchical_scraper.py "https://nilmamano.com/blog/category/dsa" 0 10

# The scraper will:
# ✅ Detect it's a WordPress blog
# ✅ Extract full article content (not just summaries)
# ✅ Format content as clean markdown
# ✅ Save results to universal_results_nilmamano.com_<timestamp>.json
```

### For Newsletter/Substack Content
```bash
# For Substack newsletter
python hierarchical_scraper.py "https://shreycation.substack.com" 0 8

# The scraper will:
# ✅ Detect Substack platform (80%+ confidence)
# ✅ Handle popups and modals automatically
# ✅ Extract full newsletter content
# ✅ Maintain proper formatting and structure
```

### For News/Tech Sites
```bash
# For news articles
python hierarchical_scraper.py "https://techcrunch.com" 0 5

# The scraper will:
# ✅ Detect WordPress platform
# ✅ Extract clean article titles
# ✅ Get article content where available
# ✅ Classify content types appropriately
```

## 🔍 Platform Detection

The scraper automatically detects and optimizes for:

- **Substack** (80-90% confidence detection)
- **Medium** (Platform-specific selectors)
- **WordPress** (Theme-agnostic extraction)
- **Ghost** (Modern blog platform)
- **Generic Blogs** (Universal fallback)

Detection includes confidence scoring and platform-specific optimizations.

## 🛡️ Advanced Features

### Full Content Extraction
- **Blog Articles**: Extracts complete article content, not just summaries
- **Markdown Formatting**: Proper headers, paragraphs, code blocks
- **Image Handling**: Includes images with proper markdown syntax
- **Clean Text**: Removes ads, navigation, and non-content elements

### Bot Evasion
- **Popup Dismissal**: Automatically removes modals and overlays
- **User-Agent Rotation**: Random, realistic browser user agents
- **Smart Headers**: Complete browser-like headers
- **Request Delays**: Intelligent delays between requests

## 📊 Success Examples

### Example 1: DSA Blog
```bash
python hierarchical_scraper.py "https://nilmamano.com/blog/category/dsa" 0 3
```
**Result**: 3 complete technical articles with full content, code examples, and proper formatting

### Example 2: Substack Newsletter
```bash
python hierarchical_scraper.py "https://shreycation.substack.com" 0 5
```
**Result**: 5 newsletter posts with full content and subscriber-only content where accessible

## 🔧 Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Some sites block scraping
   - The scraper will show: `⚠️ Error fetching URL: 403 Client Error`
   - Try a different URL or the site's /archive page

2. **Empty Results**
   - Increase `max_articles` parameter
   - Try `max_additional_pages > 0` for deeper crawling

3. **Installation Issues**
   - Make sure Python 3.7+ is installed
   - Run: `pip install --upgrade pip`
   - Then: `pip install -r requirements_blog.txt`

### Getting Help
- Check the generated JSON files for successful extractions
- Look for `📄 Extracting full content from:` messages in output
- Verify the URL is accessible in your browser

## 📁 Output Files

- `hierarchical_scraper.py` - Main scraper script
- `requirements_blog.txt` - Required Python packages
- `universal_results_*.json` - Scraping results (timestamped)
- `README.md` - This documentation

## 🤝 Contributing

Enhance the scraper by:
1. Adding new platform detection patterns
2. Improving content extraction quality
3. Enhancing bot evasion techniques
4. Expanding universal output format

## 📄 License

MIT License - see LICENSE file for details.
=======
# OGTool
A web scraper that scrapes individual websites - part of a take away test.
>>>>>>> bf70b3e259f8da8d18e2b908bb6e4919035794f9
