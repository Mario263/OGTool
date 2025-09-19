#!/usr/bin/env python3
"""
Hierarchical Card Structure Scraper - Zero-shot detection and extraction of grouped card layouts
Automatically detects topic groups, cards, and their relationships without manual configuration
"""

import json
import time
import random
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Optional, Tuple
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from markdownify import markdownify as md
from fake_useragent import UserAgent


@dataclass
class PlatformInfo:
    """Information about detected platform"""
    name: str
    confidence: float
    architecture: str
    content_selectors: Dict[str, str]
    characteristics: List[str]


@dataclass
class CardInfo:
    """Represents a single card within a topic group"""
    label: str
    main_link: str
    description: str
    secondary_links: List[Dict[str, str]]  # [{"type": "replay", "url": "...", "text": "..."}]
    metadata: Dict[str, str]  # badge counts, icons, etc.
    card_type: str  # inferred type based on content


@dataclass
class TopicGroup:
    """Represents a group of related cards (e.g., "By Company")"""
    group_type: str  # "Company", "Language", "Technical Topic", etc.
    header_text: str  # "By Company", "By Programming Language"
    anchor_id: Optional[str]  # #companies, #languages
    cards: List[CardInfo]
    group_metadata: Dict[str, str]


@dataclass
class HierarchicalStructure:
    """Complete hierarchical structure of the page"""
    page_title: str
    page_description: str
    topic_groups: List[TopicGroup]
    navigation_structure: Dict[str, str]  # anchors to sections
    metadata: Dict[str, str]


class BotEvasion:
    """Advanced bot detection evasion with realistic behavior patterns"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.visit_history = []
        self._setup_session()
    
    def _setup_session(self):
        """Configure session with realistic headers and behavior"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch page with advanced bot evasion and realistic behavior"""
        try:
            # Ensure visit_history exists
            if not hasattr(self, 'visit_history'):
                self.visit_history = []
                
            # Simulate realistic browsing patterns
            self._simulate_user_behavior(url)
            
            # Rotate user agent periodically
            if len(self.visit_history) % 3 == 0:
                self.session.headers['User-Agent'] = self.ua.random
            
            # Add realistic referer
            if self.visit_history:
                self.session.headers['Referer'] = self.visit_history[-1]
            
            # Realistic delay with some randomness
            time.sleep(random.uniform(0.8, 2.5))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Dismiss modals and popups
            soup = self._dismiss_modals_and_popups(soup)
            
            self.visit_history.append(url)
            return soup
            
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
            return None
    
    def _dismiss_modals_and_popups(self, soup):
        """Remove or simulate dismissing common modal popups and overlays"""
        # Common popup/modal selectors to remove
        popup_selectors = [
            # Substack specific
            '.modal', '.popup', '.overlay', '.subscribe-modal', '.paywall-modal',
            '.signup-modal', '.newsletter-modal', '[data-testid="signup-modal"]',
            '.sidebar-subscribe', '.subscribe-widget', '.paywall',
            '.modal-container', '.subscription-upsell', '.subscribe-step',
            
            # Generic popup patterns
            '.cookie-banner', '.cookie-consent', '.gdpr-banner',
            '.newsletter-popup', '.email-signup', '.subscription-popup',
            '.modal-backdrop', '.modal-overlay', '.popup-overlay',
            '[aria-modal="true"]', '[role="dialog"]', '.dialog',
            '.lightbox', '.overlay-container',
            
            # Common dismiss button patterns
            '.close-button', '.dismiss', '.no-thanks', '[aria-label="Close"]',
            '.modal-close', '.popup-close', '.overlay-close',
            '[data-dismiss="modal"]', '.modal-dismiss',
            
            # Specific text-based selectors
            '[aria-label="No thanks"]', '[title="Close"]', 
            'button[class*="close"]', 'button[class*="dismiss"]',
        ]
        
        removed_count = 0
        for selector in popup_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
                removed_count += 1
        
        if removed_count > 0:
            print(f"🚫 Removed {removed_count} popup/modal elements")
        
        # Also remove elements that commonly contain signup forms
        signup_selectors = [
            '.subscribe-form', '.email-capture', '.lead-magnet',
            '.signup-form', '.newsletter-form', '.subscription-form'
        ]
        
        for selector in signup_selectors:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        
        return soup
    
    def _simulate_user_behavior(self, url: str):
        """Simulate realistic user browsing behavior"""
        # Simulate mouse movements and scrolling by varying request timing
        if random.random() < 0.1:  # 10% chance of longer pause (reading)
            time.sleep(random.uniform(2, 4))
        
        # Occasionally clear and rebuild some headers (tab switching simulation)
        if random.random() < 0.05:
            self.session.headers.pop('Referer', None)


    def get_alternative_urls(self, url: str) -> List[str]:
        """Get alternative URLs to try if the main URL fails or redirects"""
        alternatives = []
        
        # For Substack sites, try the archive page
        if 'substack.com' in url:
            base_url = url.rstrip('/')
            alternatives.extend([
                f"{base_url}/archive",
                f"{base_url}/posts",
                f"{base_url}/p",
            ])
        
        # For other sites, try common alternatives
        alternatives.extend([
            f"{url.rstrip('/')}/blog",
            f"{url.rstrip('/')}/articles",
            f"{url.rstrip('/')}/posts",
        ])
        
        return alternatives


class PlatformDetector:
    """Detects content platform architecture (Substack, Medium, Ghost, etc.)"""
    
    def __init__(self):
        self.platform_signatures = {
            'substack': {
                'meta_indicators': ['substack.com', 'substack-frontend'],
                'dom_patterns': ['.post-preview', '.post-title', '.subscribe-button', '.pencraft'],
                'url_patterns': ['/p/', '/archive', '/about'],
                'characteristics': ['newsletter-style', 'subscription-focus', 'author-centric'],
                'selectors': {
                    'posts': '.post-preview, .post, article[data-testid="post-preview"], .frontend-pencraft-Box-module__box, [data-testid*="post"], .pencraft [href*="/p/"], a[href*="/p/"]',
                    'title': '.post-preview-title, .post-title, h1, h2, h3, .pencraft h1, .pencraft h2, .pencraft h3, [data-testid*="post-title"]',
                    'content': '.post-preview-content, .post-content, .available-content, .pencraft p, .post-preview-description',
                    'author': '.post-preview-byline, .byline, [data-testid="post-author"], .pencraft [href*="@"]',
                    'date': '.post-preview-date, .post-date, time, .pencraft time',
                    'interaction': '.post-preview-reactions, .post-reactions, .like-button, [data-testid*="like"], [data-testid*="comment"]'
                }
            },
            'medium': {
                'meta_indicators': ['medium.com', 'medium-frontend'],
                'dom_patterns': ['.postArticle', '.streamItem', '.js-postStream'],
                'url_patterns': ['/@', '/tagged/', '?source='],
                'characteristics': ['article-focus', 'social-features', 'clap-system'],
                'selectors': {
                    'posts': '.postArticle, .streamItem-card, article',
                    'title': '.graf--title, h1, .postArticle-title',
                    'content': '.graf, .postArticle-content, .section-content',
                    'author': '.postMetaInline-authorLockup, .author',
                    'date': '.postMetaInline time, time',
                    'interaction': '.buttonSet, .clapButton'
                }
            },
            'ghost': {
                'meta_indicators': ['ghost.io', 'ghost-frontend'],
                'dom_patterns': ['.post-card', '.post-content', '.kg-'],
                'url_patterns': ['/tag/', '/author/', '/page/'],
                'characteristics': ['modern-cms', 'member-focus', 'newsletter-integration'],
                'selectors': {
                    'posts': '.post-card, .post-preview, article',
                    'title': '.post-card-title, h1, .post-title',
                    'content': '.post-card-excerpt, .post-content, .kg-card',
                    'author': '.post-card-meta .author, .author-card',
                    'date': '.post-card-meta time, time',
                    'interaction': '.post-card-readmore, .read-more'
                }
            },
            'wordpress': {
                'meta_indicators': ['wp-content', 'wordpress'],
                'dom_patterns': ['.post', '.entry', '.wp-block'],
                'url_patterns': ['/wp-content/', '/category/', '/?p='],
                'characteristics': ['flexible-cms', 'plugin-ecosystem', 'theme-variety'],
                'selectors': {
                    'posts': '.post, .entry, article',
                    'title': '.entry-title, h1, .post-title',
                    'content': '.entry-content, .post-content, .content',
                    'author': '.author, .byline, .post-author',
                    'date': '.entry-date, .post-date, time',
                    'interaction': '.entry-meta, .post-meta'
                }
            },
            'generic_blog': {
                'meta_indicators': [],
                'dom_patterns': ['.post', '.article', '.blog'],
                'url_patterns': ['/blog/', '/posts/', '/articles/'],
                'characteristics': ['custom-build', 'varied-structure'],
                'selectors': {
                    'posts': '.post, .article, article, .blog-post',
                    'title': 'h1, h2, .title, .post-title',
                    'content': '.content, .post-content, .article-content',
                    'author': '.author, .byline, .writer',
                    'date': '.date, time, .published',
                    'interaction': '.meta, .post-meta, .article-meta'
                }
            }
        }
    
    def detect_platform(self, soup: BeautifulSoup, url: str) -> PlatformInfo:
        """Detect the platform architecture of the website"""
        scores = {}
        
        for platform_name, signature in self.platform_signatures.items():
            score = 0
            found_characteristics = []
            
            # Check URL patterns
            for pattern in signature['url_patterns']:
                if pattern in url:
                    score += 2
                    found_characteristics.append(f"url_pattern:{pattern}")
            
            # Check meta indicators
            page_html = str(soup)
            for indicator in signature['meta_indicators']:
                if indicator in page_html.lower():
                    score += 3
                    found_characteristics.append(f"meta:{indicator}")
            
            # Check DOM patterns
            for pattern in signature['dom_patterns']:
                elements = soup.select(pattern)
                if elements:
                    score += len(elements[:3])  # Cap at 3 to avoid skewing
                    found_characteristics.append(f"dom:{pattern}({len(elements)})")
            
            scores[platform_name] = {
                'score': score,
                'characteristics': found_characteristics
            }
        
        # Find the best match
        best_platform = max(scores.keys(), key=lambda k: scores[k]['score'])
        best_score = scores[best_platform]['score']
        
        # Calculate confidence (normalize score)
        max_possible_score = 10  # Rough estimate
        confidence = min(best_score / max_possible_score, 1.0)
        
        platform_data = self.platform_signatures[best_platform]
        
        return PlatformInfo(
            name=best_platform,
            confidence=confidence,
            architecture=platform_data['characteristics'][0] if platform_data['characteristics'] else 'unknown',
            content_selectors=platform_data['selectors'],
            characteristics=scores[best_platform]['characteristics']
        )


class HierarchicalStructureDetector:
    """Detects hierarchical card-based structures like topic groups with cards"""
    
    def __init__(self):
        self.group_indicators = [
            'by company', 'by programming language', 'by language', 'by technical topic',
            'by topic', 'companies', 'languages', 'topics', 'categories', 'sections',
            'programming languages', 'technical topics', 'interview topics'
        ]
        
        self.card_indicators = [
            'card', 'item', 'tile', 'box', 'entry', 'topic', 'company', 'language'
        ]
    
    def detect_hierarchical_structure(self, soup: BeautifulSoup, url: str, max_articles: int = 20) -> HierarchicalStructure:
        """Detect and extract hierarchical card structure"""
        print("🔍 Detecting hierarchical structure...")
        
        # Enhanced blog listing detection
        blog_articles = self._detect_blog_articles(soup, max_articles)
        if blog_articles:
            print(f"📰 Detected blog listing page with {len(blog_articles)} articles")
            return self._create_blog_structure(soup, url, blog_articles)
        
        # Extract page metadata
        page_title = self._extract_page_title(soup)
        page_description = self._extract_page_description(soup)
        
        # Find navigation structure
        navigation_structure = self._detect_navigation_anchors(soup)
        
        # Detect topic groups
        topic_groups = self._detect_topic_groups(soup, url)
        
        print(f"📊 Found {len(topic_groups)} topic groups")
        for group in topic_groups:
            print(f"  - {group.header_text}: {len(group.cards)} cards")
        
        return HierarchicalStructure(
            page_title=page_title,
            page_description=page_description,
            topic_groups=topic_groups,
            navigation_structure=navigation_structure,
            metadata={}
        )
    
    def _extract_page_title(self, soup: BeautifulSoup) -> str:
        """Extract main page title"""
        # Try multiple title strategies
        title_selectors = [
            'h1', '.page-title', '.main-title', 'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return "Untitled Page"
    
    def _extract_page_description(self, soup: BeautifulSoup) -> str:
        """Extract page description or subtitle"""
        desc_selectors = [
            '.page-description', '.subtitle', 'p.lead', '.intro',
            'meta[name="description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '')
                else:
                    text = element.get_text(strip=True)
                    if len(text) > 20:
                        return text
        
        return ""
    
    def _detect_navigation_anchors(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Detect navigation anchors that link to sections"""
        navigation = {}
        
        # Find navigation links that point to page anchors
        nav_links = soup.select('nav a[href^="#"], .nav a[href^="#"], .table-of-contents a[href^="#"]')
        
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href and text:
                navigation[href] = text
        
        return navigation
    
    def _detect_topic_groups(self, soup: BeautifulSoup, url: str) -> List[TopicGroup]:
        """Detect topic groups and their associated cards"""
        topic_groups = []
        
        # Strategy 1: Look for explicit section headers
        groups_by_headers = self._find_groups_by_headers(soup, url)
        topic_groups.extend(groups_by_headers)
        
        # Strategy 2: Look for repeated card patterns with implicit groupings
        if not topic_groups:
            groups_by_patterns = self._find_groups_by_patterns(soup, url)
            topic_groups.extend(groups_by_patterns)
        
        # Strategy 3: Fallback to single group with all cards
        if not topic_groups:
            single_group = self._create_single_group_fallback(soup, url)
            if single_group:
                topic_groups.append(single_group)
        
        return topic_groups
    
    def _find_groups_by_headers(self, soup: BeautifulSoup, url: str) -> List[TopicGroup]:
        """Find topic groups by looking for section headers"""
        groups = []
        
        # Find potential group headers
        header_candidates = []
        
        # Look for headings that match group patterns
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True).lower()
            if any(indicator in text for indicator in self.group_indicators):
                header_candidates.append(heading)
        
        # Process each header and find its associated cards
        for header in header_candidates:
            group = self._extract_group_from_header(header, soup, url)
            if group and group.cards:
                groups.append(group)
        
        return groups
    
    def _extract_group_from_header(self, header: Tag, soup: BeautifulSoup, url: str) -> Optional[TopicGroup]:
        """Extract a topic group starting from a header element"""
        header_text = header.get_text(strip=True)
        
        # Determine group type from header text
        group_type = self._determine_group_type(header_text)
        
        # Find the section containing cards after this header
        cards_container = self._find_cards_container_after_header(header)
        
        if not cards_container:
            return None
        
        # Extract cards from the container
        cards = self._extract_cards_from_container(cards_container, url)
        
        # Get anchor ID if available
        anchor_id = None
        if header.get('id'):
            anchor_id = f"#{header.get('id')}"
        
        return TopicGroup(
            group_type=group_type,
            header_text=header_text,
            anchor_id=anchor_id,
            cards=cards,
            group_metadata={}
        )
    
    def _determine_group_type(self, header_text: str) -> str:
        """Determine the type of group from header text"""
        text_lower = header_text.lower()
        
        if 'company' in text_lower or 'companies' in text_lower:
            return 'Company'
        elif 'language' in text_lower or 'programming' in text_lower:
            return 'Programming Language'
        elif 'technical' in text_lower or 'topic' in text_lower:
            return 'Technical Topic'
        elif 'interview' in text_lower:
            return 'Interview Resource'
        else:
            return 'General'
    
    def _find_cards_container_after_header(self, header: Tag) -> Optional[Tag]:
        """Find the container holding cards after a header"""
        # Look for containers in the following siblings
        current = header.next_sibling
        
        while current:
            if isinstance(current, Tag):
                # Check if this element contains multiple card-like children
                potential_cards = self._find_potential_cards(current)
                if len(potential_cards) >= 2:  # At least 2 cards to be considered a group
                    return current
                
                # If it's another header, stop looking
                if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
            
            current = current.next_sibling
        
        # If not found in siblings, look in parent's following siblings
        parent = header.parent
        if parent:
            current = parent.next_sibling
            while current:
                if isinstance(current, Tag):
                    potential_cards = self._find_potential_cards(current)
                    if len(potential_cards) >= 2:
                        return current
                    
                    # If it's another section header, stop
                    if current.find(['h1', 'h2', 'h3']):
                        break
                
                current = current.next_sibling
        
        return None
    
    def _find_potential_cards(self, container: Tag) -> List[Tag]:
        """Find potential card elements within a container"""
        potential_cards = []
        
        # Look for direct children that could be cards
        for child in container.children:
            if isinstance(child, Tag):
                # Check if child looks like a card
                if self._looks_like_card(child):
                    potential_cards.append(child)
        
        # If no direct children found, look deeper
        if not potential_cards:
            # Look for elements with card-like classes
            card_candidates = container.find_all(attrs={'class': re.compile(r'(card|item|tile|topic|company|language)', re.I)})
            
            # Filter for elements that contain links
            for candidate in card_candidates:
                if candidate.find('a'):
                    potential_cards.append(candidate)
        
        # Alternative: look for repeated link patterns
        if not potential_cards:
            links = container.find_all('a', href=True)
            if len(links) >= 2:
                # Group links that have similar structure/context
                link_groups = self._group_similar_links(links)
                for group in link_groups:
                    if len(group) >= 2:
                        potential_cards.extend([link.parent for link in group if link.parent])
        
        return potential_cards
    
    def _looks_like_card(self, element: Tag) -> bool:
        """Check if an element looks like a card"""
        # Check classes
        classes = ' '.join(element.get('class', [])).lower()
        if any(indicator in classes for indicator in self.card_indicators):
            return True
        
        # Check if it contains a link (most cards do)
        if not element.find('a'):
            return False
        
        # Check if it has enough content to be a card
        text_content = element.get_text(strip=True)
        if len(text_content) < 5:
            return False
        
        # Check for card-like structure (title + description or multiple links)
        links = element.find_all('a')
        headings = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        return len(links) >= 1 and (len(headings) >= 1 or len(links) >= 2)
    
    def _group_similar_links(self, links: List[Tag]) -> List[List[Tag]]:
        """Group links that have similar context or patterns"""
        groups = []
        processed = set()
        
        for link in links:
            if link in processed:
                continue
            
            group = [link]
            processed.add(link)
            
            # Find similar links
            for other_link in links:
                if other_link in processed:
                    continue
                
                if self._links_are_similar(link, other_link):
                    group.append(other_link)
                    processed.add(other_link)
            
            if len(group) >= 2:
                groups.append(group)
        
        return groups
    
    def _links_are_similar(self, link1: Tag, link2: Tag) -> bool:
        """Check if two links have similar context/structure"""
        # Check if they have similar parent classes
        parent1_classes = set(link1.parent.get('class', []) if link1.parent else [])
        parent2_classes = set(link2.parent.get('class', []) if link2.parent else [])
        
        if parent1_classes and parent2_classes and parent1_classes == parent2_classes:
            return True
        
        # Check if they have similar href patterns
        href1 = link1.get('href', '')
        href2 = link2.get('href', '')
        
        if href1 and href2:
            # Similar path structure
            path1_parts = [part for part in href1.split('/') if part]
            path2_parts = [part for part in href2.split('/') if part]
            
            if len(path1_parts) == len(path2_parts) and len(path1_parts) > 0:
                # Check if they share common path prefixes
                common_parts = sum(1 for p1, p2 in zip(path1_parts[:-1], path2_parts[:-1]) if p1 == p2)
                return common_parts >= max(1, len(path1_parts) - 2)
        
        return False
    
    def _extract_cards_from_container(self, container: Tag, url: str) -> List[CardInfo]:
        """Extract card information from a container"""
        cards = []
        potential_cards = self._find_potential_cards(container)
        
        for card_element in potential_cards:
            card_info = self._extract_single_card(card_element, url)
            if card_info:
                cards.append(card_info)
        
        return cards
    
    def _extract_single_card(self, card_element: Tag, url: str) -> Optional[CardInfo]:
        """Extract information from a single card element"""
        # Extract label (usually the main text or heading)
        label = self._extract_card_label(card_element)
        if not label:
            return None
        
        # Extract main link
        main_link = self._extract_main_link(card_element, url)
        if not main_link:
            return None
        
        # Extract description
        description = self._extract_card_description(card_element)
        
        # Extract secondary links
        secondary_links = self._extract_secondary_links(card_element, url, main_link)
        
        # Extract metadata (badges, counts, etc.)
        metadata = self._extract_card_metadata(card_element)
        
        # Determine card type
        card_type = self._determine_card_type(label, main_link, card_element)
        
        return CardInfo(
            label=label,
            main_link=main_link,
            description=description,
            secondary_links=secondary_links,
            metadata=metadata,
            card_type=card_type
        )
    
    def _extract_card_label(self, card_element: Tag) -> str:
        """Extract the main label/title of a card"""
        # Try headings first
        for heading in card_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = heading.get_text(strip=True)
            if text:
                return text
        
        # Try elements with title-like classes
        title_selectors = [
            '.title', '.name', '.label', '.heading', '.card-title',
            '.topic-name', '.company-name', '.language-name'
        ]
        
        for selector in title_selectors:
            element = card_element.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        
        # Try main link text
        main_link = card_element.find('a')
        if main_link:
            link_text = main_link.get_text(strip=True)
            # Only use if it's not too generic
            if link_text and not any(generic in link_text.lower() for generic in ['click', 'here', 'link', 'read more']):
                return link_text
        
        # Advanced parsing for cards with combined text
        all_text = card_element.get_text(strip=True)
        
        # Try to extract just the company/topic name from combined text
        # Pattern: "CompanyNameDescription" or "TopicNameDescription"
        
        # Strategy 1: Look for known company names
        company_names = [
            'Google', 'Meta', 'Facebook', 'Amazon', 'Microsoft', 'Apple', 'Netflix',
            'Uber', 'Airbnb', 'Tesla', 'Twitter', 'LinkedIn', 'Spotify', 'Stripe',
            'Palantir', 'Snowflake', 'OpenAI', 'Nvidia', 'Salesforce', 'Adobe',
            'ByteDance', 'TikTok', 'Snap', 'Shopify', 'Slack', 'Dropbox'
        ]
        
        for company in company_names:
            if all_text.startswith(company):
                return company
        
        # Strategy 2: Look for programming language patterns
        if any(lang in all_text for lang in ['JavaScript', 'Python', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Ruby']):
            language_match = re.search(r'^(JavaScript|Python|Java|C\+\+|C#|Go|Rust|Swift|Ruby)', all_text)
            if language_match:
                return language_match.group(1)
        
        # Strategy 3: Extract technical topic names
        # Look for capitalized words at the beginning
        topic_match = re.search(r'^([A-Z][a-z]*(?:\s+[A-Z][a-z]*)*)', all_text)
        if topic_match:
            potential_topic = topic_match.group(1)
            # Make sure it's not too long (likely includes description)
            if len(potential_topic.split()) <= 3:
                return potential_topic
        
        # Strategy 4: Try to extract name before common description patterns
        desc_patterns = ['Interview', 'Questions', 'Tips', 'Watch']
        for pattern in desc_patterns:
            if pattern in all_text:
                parts = all_text.split(pattern, 1)
                if parts[0].strip():
                    potential_name = parts[0].strip()
                    # Remove trailing non-alphanumeric characters
                    potential_name = re.sub(r'[^\w\s]+$', '', potential_name)
                    if potential_name and len(potential_name) <= 30:
                        return potential_name
        
        # Fallback to first few words
        words = all_text.split()
        if words:
            # Take first few words that form a reasonable title
            title_words = []
            for word in words[:3]:  # Limit to 3 words max
                title_words.append(word)
                if len(' '.join(title_words)) > 25:
                    break
            return ' '.join(title_words)
        
        return ""
    
    def _extract_main_link(self, card_element: Tag, url: str) -> str:
        """Extract the main/primary link from a card"""
        links = card_element.find_all('a', href=True)
        
        if not links:
            return ""
        
        # If only one link, that's the main one
        if len(links) == 1:
            return urljoin(url, links[0].get('href'))
        
        # Multiple links: try to identify the main one
        main_link_candidates = []
        
        for link in links:
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            classes = ' '.join(link.get('class', [])).lower()
            
            # Score based on various factors
            score = 0
            
            # Primary link indicators
            if 'main' in classes or 'primary' in classes or 'title' in classes:
                score += 3
            
            # Link text quality
            if 'interview' in text or 'guide' in text or 'process' in text:
                score += 2
            elif 'questions' in text:
                score += 1
            
            # Avoid secondary link patterns
            if 'watch' in text or 'replay' in text or 'video' in text:
                score -= 1
            
            # Longer, more descriptive text is usually main
            if len(text) > 10:
                score += 1
            
            main_link_candidates.append((link, score))
        
        # Return highest scoring link
        main_link_candidates.sort(key=lambda x: x[1], reverse=True)
        return urljoin(url, main_link_candidates[0][0].get('href'))
    
    def _extract_card_description(self, card_element: Tag) -> str:
        """Extract description text from a card"""
        # Strategy 1: Look for description-like elements
        desc_selectors = [
            '.description', '.desc', '.summary', '.subtitle',
            '.card-description', '.card-text', 'p'
        ]
        
        for selector in desc_selectors:
            element = card_element.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 5:
                    return text
        
        # Strategy 2: Parse description from card text patterns
        all_text = card_element.get_text(strip=True)
        
        # Look for common description patterns
        description_patterns = [
            r'Interview process\s*&\s*questions',
            r'Questions\s*&\s*tips',
            r'Interview\s*questions',
            r'Technical\s*interview',
            r'Coding\s*interview',
            r'System\s*design',
            r'Behavioral\s*interview'
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Strategy 3: Look for text between known company/topic names and "Watch" keyword
        # This handles cases like "GoogleInterview process& questionsWatch"
        if 'watch' in all_text.lower():
            # Split by 'Watch' and take the part before it
            parts = re.split(r'watch', all_text, flags=re.IGNORECASE)
            if len(parts) > 1:
                before_watch = parts[0].strip()
                
                # Extract description part (everything after company/topic name)
                # Look for common company/topic indicators
                name_patterns = [
                    r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',  # Company names like "Google", "Meta", etc.
                    r'^[A-Z#]+',  # Language names like "C++", "C#"
                    r'^\w+',  # Single word topics
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, before_watch)
                    if match:
                        name_end = match.end()
                        potential_desc = before_watch[name_end:].strip()
                        
                        # Clean up the description
                        potential_desc = re.sub(r'^[^\w]*', '', potential_desc)  # Remove leading non-word chars
                        if len(potential_desc) > 3:
                            return potential_desc
        
        # Strategy 4: Look for text that follows the main heading/title
        headings = card_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            # Find text after the first heading
            heading = headings[0]
            next_element = heading.next_sibling
            while next_element:
                if isinstance(next_element, NavigableString):
                    text = next_element.strip()
                    if len(text) > 5:
                        return text
                elif isinstance(next_element, Tag) and next_element.name in ['p', 'div', 'span']:
                    text = next_element.get_text(strip=True)
                    if len(text) > 5 and next_element != heading:
                        return text
                next_element = next_element.next_sibling
        
        return ""
    
    def _extract_secondary_links(self, card_element: Tag, url: str, main_link: str) -> List[Dict[str, str]]:
        """Extract secondary links (like replay links, question links)"""
        secondary_links = []
        links = card_element.find_all('a', href=True)
        
        for link in links:
            href = urljoin(url, link.get('href'))
            if href == main_link:
                continue  # Skip the main link
            
            text = link.get_text(strip=True)
            link_type = self._classify_secondary_link(text, href)
            
            if link_type:
                secondary_links.append({
                    'type': link_type,
                    'url': href,
                    'text': text
                })
        
        return secondary_links
    
    def _classify_secondary_link(self, text: str, href: str) -> Optional[str]:
        """Classify the type of secondary link"""
        text_lower = text.lower()
        href_lower = href.lower()
        
        if 'watch' in text_lower or 'replay' in text_lower or 'video' in text_lower:
            return 'replay'
        elif 'question' in text_lower or 'problems' in text_lower:
            return 'questions'
        elif 'tip' in text_lower or 'advice' in text_lower:
            return 'tips'
        elif 'mock' in href_lower or 'practice' in text_lower:
            return 'practice'
        elif 'guide' in text_lower or 'tutorial' in text_lower:
            return 'guide'
        else:
            return 'other'
    
    def _extract_card_metadata(self, card_element: Tag) -> Dict[str, str]:
        """Extract metadata like counts, badges, etc."""
        metadata = {}
        
        # Look for count indicators
        text = card_element.get_text()
        count_matches = re.findall(r'(\d+)\s*(replay|interview|question|video)', text, re.I)
        
        for count, item_type in count_matches:
            metadata[f"{item_type.lower()}_count"] = count
        
        # Look for badge-like elements
        badges = card_element.find_all(attrs={'class': re.compile(r'(badge|tag|label)', re.I)})
        if badges:
            badge_texts = [badge.get_text(strip=True) for badge in badges]
            metadata['badges'] = badge_texts
        
        return metadata
    
    def _determine_card_type(self, label: str, main_link: str, card_element: Tag) -> str:
        """Determine the type of card based on its content"""
        label_lower = label.lower()
        link_lower = main_link.lower()
        
        # Company names patterns
        company_indicators = ['google', 'meta', 'facebook', 'amazon', 'microsoft', 'apple', 'netflix']
        if any(company in label_lower for company in company_indicators):
            return 'company'
        
        # Programming language patterns
        language_indicators = ['python', 'java', 'javascript', 'c++', 'go', 'rust', 'swift']
        if any(lang in label_lower for lang in language_indicators):
            return 'programming_language'
        
        # Technical topic patterns
        tech_indicators = ['algorithm', 'data structure', 'system design', 'tree', 'graph', 'array']
        if any(tech in label_lower for tech in tech_indicators):
            return 'technical_topic'
        
        # URL-based classification
        if '/guides/hiring-process/' in link_lower:
            return 'company'
        elif 'interview-questions' in link_lower:
            return 'question_set'
        
        return 'general'
    
    def _find_groups_by_patterns(self, soup: BeautifulSoup, url: str) -> List[TopicGroup]:
        """Find groups by analyzing repeating patterns when headers aren't clear"""
        # This is a fallback method for when explicit headers aren't found
        # Look for containers with multiple similar elements
        
        potential_containers = soup.find_all(['div', 'section', 'ul', 'ol'])
        
        for container in potential_containers:
            potential_cards = self._find_potential_cards(container)
            if len(potential_cards) >= 3:  # At least 3 cards to form a group
                cards = self._extract_cards_from_container(container, url)
                if cards:
                    # Try to infer group type from cards
                    group_type = self._infer_group_type_from_cards(cards)
                    
                    group = TopicGroup(
                        group_type=group_type,
                        header_text=f"Detected {group_type} Group",
                        anchor_id=None,
                        cards=cards,
                        group_metadata={}
                    )
                    return [group]  # Return first successful group
        
        return []
    
    def _infer_group_type_from_cards(self, cards: List[CardInfo]) -> str:
        """Infer group type by analyzing the cards within it"""
        card_types = [card.card_type for card in cards]
        type_counts = Counter(card_types)
        
        if type_counts.most_common(1):
            most_common_type = type_counts.most_common(1)[0][0]
            if most_common_type == 'company':
                return 'Company'
            elif most_common_type == 'programming_language':
                return 'Programming Language'
            elif most_common_type == 'technical_topic':
                return 'Technical Topic'
        
        return 'Mixed Content'
    
    def _create_single_group_fallback(self, soup: BeautifulSoup, url: str) -> Optional[TopicGroup]:
        """Create a single group containing all found cards as fallback"""
        # Find all potential cards across the entire page
        all_potential_cards = []
        
        # Look in main content areas
        main_areas = soup.find_all(['main', 'article', '.content', '.main-content'])
        if not main_areas:
            main_areas = [soup.find('body')]
        
        for area in main_areas:
            if area:
                potential_cards = self._find_potential_cards(area)
                all_potential_cards.extend(potential_cards)
        
        if len(all_potential_cards) >= 2:
            cards = []
            for card_element in all_potential_cards[:20]:  # Limit to avoid too many
                card_info = self._extract_single_card(card_element, url)
                if card_info:
                    cards.append(card_info)
            
            if cards:
                return TopicGroup(
                    group_type='General',
                    header_text='All Items',
                    anchor_id=None,
                    cards=cards,
                    group_metadata={}
                )
        
        return None

    def _detect_blog_articles(self, soup: BeautifulSoup, max_articles: int = 20) -> List[Dict]:
        """Detect blog article listings with enhanced pattern matching"""
        articles = []
        
        # Enhanced blog article selectors for various layouts
        article_selectors = [
            # Generic article selectors
            'article', '.post', '.blog-post', '.entry', '.article',
            # Card-based layouts
            '.card:has(a[href*="/blog"]), .card:has(a[href*="/post"]), .card:has(a[href*="/article"])',
            # List-based layouts
            '.post-item', '.blog-item', '.article-item', '.entry-item',
            # Modern frameworks and link-based detection
            'a[href*="/blogs/"]',  # Direct blog links
            'a[href*="/blog/"]',   # Alternative blog path
            'a[href*="/post/"]',   # Post links
            # Content containers with links
            'div:has(a[href*="/blog"]), div:has(a[href*="/post"]), li:has(a[href*="/blog"])',
            # Specific blog platforms
            '.substack-post', '.medium-post', '.ghost-post'
        ]
        
        # Find potential article containers
        for selector in article_selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:max_articles * 2]:  # Allow more elements to process
                    if selector.startswith('a[href'):
                        # For direct link selectors, treat the element as the link
                        article_data = self._extract_article_from_link(element, soup)
                    else:
                        article_data = self._extract_article_data(element)
                    
                    if article_data and article_data not in articles:
                        articles.append(article_data)
                        if len(articles) >= max_articles:
                            break
                
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                continue
        
        # If no articles found with selectors, try link-based detection
        if not articles:
            articles = self._detect_articles_by_links(soup, max_articles)
        
        return articles[:max_articles]
    
    def _extract_article_from_link(self, link_elem: Tag, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract article data directly from a link element"""
        url = link_elem.get('href')
        if not url or not self._is_article_link(url):
            return None
        
        # Extract title from link text or nearby elements
        raw_title = link_elem.get_text(strip=True)
        
        # Clean the title using our new cleaning logic
        title = self._clean_article_title(raw_title)
        
        # If title is too short after cleaning, look for title in parent or nearby elements
        if not title or len(title) < 10:
            parent = link_elem.find_parent(['div', 'article', 'section', 'li'])
            if parent:
                # Look for headings near the link
                for heading in parent.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    heading_text = heading.get_text(strip=True)
                    if heading_text and len(heading_text) > len(title):
                        title = self._clean_article_title(heading_text)
                        break
        
        if not title or len(title) < 5:
            return None
        
        # Extract description from the raw link text using our new extraction logic
        description = self._extract_description_from_text(raw_title)
        
        # Extract metadata from the raw text and parent elements
        metadata = {}
        if raw_title:
            extracted_date = self._extract_date_from_text(raw_title)
            if extracted_date:
                metadata['date'] = extracted_date
            
            if 'Franchise Strategies' in raw_title:
                metadata['category'] = 'Franchise Strategies'
        
        return {
            'title': title,
            'url': url,
            'description': description,
            'metadata': metadata
        }
    
    def _extract_article_data(self, element: Tag) -> Optional[Dict]:
        """Extract data from a potential article element"""
        # Find the main link
        link_elem = element.find('a', href=True)
        if not link_elem:
            return None
        
        url = link_elem.get('href')
        if not url:
            return None
        
        # Filter out non-article links
        if not self._is_article_link(url):
            return None
        
        # Extract title
        title = self._extract_article_title(element, link_elem)
        if not title or len(title) < 3:
            return None
        
        # Extract description/excerpt
        description = self._extract_article_description(element)
        
        # Extract metadata
        metadata = self._extract_article_metadata(element)
        
        return {
            'title': title,
            'url': url,  # Will be normalized later in the process
            'description': description,
            'metadata': metadata
        }
    
    def _is_article_link(self, url: str) -> bool:
        """Check if URL likely points to an article"""
        url_lower = url.lower()
        
        # Positive indicators
        article_indicators = [
            '/blog/', '/post/', '/article/', '/news/', '/p/',
            'blog', 'post', 'article', 'story'
        ]
        
        # Negative indicators
        exclude_indicators = [
            '/tag/', '/category/', '/author/', '/search/', '/page/',
            'javascript:', 'mailto:', '#', '/privacy', '/terms',
            '.pdf', '.jpg', '.png', '.gif', '.css', '.js'
        ]
        
        # Check exclusions first
        if any(exclude in url_lower for exclude in exclude_indicators):
            return False
        
        # Check positive indicators
        return any(indicator in url_lower for indicator in article_indicators)
    
    def _extract_article_title(self, element: Tag, link_elem: Tag) -> str:
        """Extract article title from element"""
        # Try multiple title extraction strategies
        title_selectors = [
            'h1', 'h2', 'h3', '.title', '.headline', '.post-title',
            '.entry-title', '.article-title', '.card-title'
        ]
        
        # Try finding title in child elements
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    return self._clean_article_title(title)
        
        # Fallback to link text but clean it up
        title = link_elem.get_text(strip=True)
        return self._clean_article_title(title) if title and len(title) > 3 else ""
    
    def _clean_article_title(self, raw_title: str) -> str:
        """Clean up article title by removing metadata and descriptions"""
        if not raw_title:
            return ""
        
        # Common patterns to split on
        split_patterns = [
            'Franchise Strategies',  # Category separator
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',  # Date patterns
            r'\d{4}-\d{2}-\d{2}',  # ISO date format
            r'\b\d{1,2}/\d{1,2}/\d{4}',  # Date format MM/DD/YYYY
        ]
        
        # Split on the first pattern found
        for pattern in split_patterns:
            if 'Franchise Strategies' in pattern:
                # Simple string split for category
                if pattern in raw_title:
                    title_part = raw_title.split(pattern)[0].strip()
                    if len(title_part) > 5:
                        return title_part
            else:
                # Regex split for date patterns
                import re
                match = re.search(pattern, raw_title)
                if match:
                    title_part = raw_title[:match.start()].strip()
                    if len(title_part) > 5:
                        return title_part
        
        # If no patterns found, try to extract the first meaningful sentence
        # Look for the first sentence that's longer than 10 chars but less than 120 chars
        sentences = raw_title.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if 10 < len(sentence) < 120 and not any(word in sentence.lower() for word in ['click', 'read more', 'continue']):
                return sentence
        
        # Last resort: take first 100 characters and find a good break point
        if len(raw_title) > 100:
            truncated = raw_title[:100]
            # Find last space to avoid cutting words
            last_space = truncated.rfind(' ')
            if last_space > 50:
                return truncated[:last_space].strip()
        
        return raw_title.strip()
    
    def _extract_article_description(self, element: Tag) -> str:
        """Extract article description/excerpt"""
        desc_selectors = [
            '.excerpt', '.description', '.summary', '.preview',
            '.card-text', '.post-excerpt', 'p', '.content'
        ]
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                desc = desc_elem.get_text(strip=True)
                # Filter out very short or very long descriptions
                if 10 < len(desc) < 500:
                    return desc
        
        # If no description found in structured elements, try to extract from link text
        link_text = element.get_text(strip=True) if element else ""
        if link_text:
            return self._extract_description_from_text(link_text)
        
        return ""
    
    def _extract_description_from_text(self, text: str) -> str:
        """Extract description from concatenated text like the franchise blog format"""
        if not text:
            return ""
        
        # Split by common patterns to find the description part
        patterns = [
            'Franchise Strategies',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
        ]
        
        import re
        
        # Find the category and date positions
        category_pos = text.find('Franchise Strategies')
        date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},?\s*\d{4}', text)
        
        if category_pos > 0 and date_match:
            # Extract text after the date
            after_date = text[date_match.end():].strip()
            if len(after_date) > 20:
                # Clean up the description
                description = after_date
                # Remove common trailing phrases
                for phrase in ['Learn more', 'Read more', 'Continue reading', 'Click here']:
                    if description.lower().endswith(phrase.lower()):
                        description = description[:-len(phrase)].strip()
                
                # Limit length to reasonable description size
                if len(description) > 300:
                    # Find a good break point
                    sentences = description.split('.')
                    if len(sentences) > 1:
                        description = '.'.join(sentences[:2]) + '.'
                    else:
                        description = description[:300].strip()
                        last_space = description.rfind(' ')
                        if last_space > 200:
                            description = description[:last_space].strip()
                
                return description
        
        # Fallback: if the pattern doesn't work, try to extract any meaningful description
        # Look for text that appears to be a description (longer phrases)
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for sentences that seem like descriptions (not dates, categories, or titles)
            if (50 < len(sentence) < 300 and 
                not re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d', sentence) and
                'Franchise Strategies' not in sentence and
                not sentence.lower().startswith(('click', 'read', 'learn'))):
                return sentence + '.'
        
        return ""
    
    def _extract_article_metadata(self, element: Tag) -> Dict:
        """Extract article metadata (date, category, etc.)"""
        metadata = {}
        
        # Extract date from structured elements first
        date_selectors = [
            'time', '.date', '.published', '.post-date',
            '[datetime]', '.timestamp'
        ]
        
        for selector in date_selectors:
            date_elem = element.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if date_text:
                    metadata['date'] = date_text
                    break
        
        # If no structured date found, extract from text content
        if 'date' not in metadata:
            text_content = element.get_text(strip=True) if element else ""
            extracted_date = self._extract_date_from_text(text_content)
            if extracted_date:
                metadata['date'] = extracted_date
        
        # Extract category from structured elements
        category_selectors = [
            '.category', '.tag', '.label', '.badge'
        ]
        
        for selector in category_selectors:
            cat_elem = element.select_one(selector)
            if cat_elem:
                category = cat_elem.get_text(strip=True)
                if category:
                    metadata['category'] = category
                    break
        
        # If no structured category found, extract from text content
        if 'category' not in metadata:
            text_content = element.get_text(strip=True) if element else ""
            if 'Franchise Strategies' in text_content:
                metadata['category'] = 'Franchise Strategies'
        
        return metadata
    
    def _extract_date_from_text(self, text: str) -> str:
        """Extract date from text content"""
        if not text:
            return ""
        
        import re
        
        # Look for common date patterns
        date_patterns = [
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},?\s*\d{4}',
            r'\b\d{1,2}/\d{1,2}/\d{4}',
            r'\b\d{4}-\d{2}-\d{2}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def _detect_articles_by_links(self, soup: BeautifulSoup, max_articles: int) -> List[Dict]:
        """Fallback method: detect articles by analyzing all links"""
        articles = []
        
        # Find all links that might be articles
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            url = link.get('href')
            if not self._is_article_link(url):
                continue
            
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            
            # Try to find description in parent container
            parent = link.find_parent(['div', 'article', 'li', 'section'])
            description = ""
            if parent:
                # Look for description in siblings or parent
                for p in parent.find_all('p'):
                    p_text = p.get_text(strip=True)
                    if 10 < len(p_text) < 300 and p_text != title:
                        description = p_text
                        break
            
            articles.append({
                'title': title,
                'url': url,
                'description': description,
                'metadata': {}
            })
            
            if len(articles) >= max_articles:
                break
        
        return articles
    
    def _create_blog_structure(self, soup: BeautifulSoup, url: str, blog_articles: List[Dict]) -> HierarchicalStructure:
        """Create hierarchical structure for blog listings"""
        page_title = self._extract_page_title(soup)
        page_description = self._extract_page_description(soup)
        
        # Convert articles to cards with normalized URLs
        cards = []
        for article in blog_articles:
            # Normalize the URL to be absolute
            article_url = article['url']
            if article_url.startswith('./'):
                article_url = urljoin(url, article_url[2:])
            elif article_url.startswith('/'):
                article_url = urljoin(url, article_url)
            elif not article_url.startswith(('http://', 'https://')):
                article_url = urljoin(url, article_url)
            
            card = CardInfo(
                label=article['title'],
                main_link=article_url,
                description=article['description'],
                secondary_links=[],
                metadata=article['metadata'],
                card_type='blog_article'
            )
            cards.append(card)
        
        # Create single topic group for blog articles
        topic_group = TopicGroup(
            group_type='Blog Articles',
            header_text=f'Blog Articles ({len(cards)} found)',
            anchor_id=None,
            cards=cards,
            group_metadata={'total_articles': len(cards)}
        )
        
        return HierarchicalStructure(
            page_title=page_title,
            page_description=page_description,
            topic_groups=[topic_group],
            navigation_structure={},
            metadata={'article_count': len(cards), 'page_type': 'blog_listing'}
        )


class HierarchicalContentExtractor:
    """Extract content while preserving hierarchical structure"""
    
    def __init__(self, bot_evasion=None):
        self.bot_evasion = bot_evasion or BotEvasion()
    
    def extract_hierarchical_content(self, soup: BeautifulSoup, url: str, max_articles: int = 20) -> Dict:
        """Extract content organized by hierarchical structure with platform awareness"""
        # Detect platform architecture
        platform_detector = PlatformDetector()
        platform_info = platform_detector.detect_platform(soup, url)
        
        print(f"🔍 Detected platform: {platform_info.name} (confidence: {platform_info.confidence:.2f})")
        if platform_info.characteristics:
            print(f"   Characteristics: {', '.join(platform_info.characteristics[:3])}")
        
        # Use platform-specific extraction for known platforms
        if platform_info.name in ['substack', 'medium', 'ghost'] and platform_info.confidence > 0.3:
            structure = self._extract_platform_content(soup, url, platform_info, max_articles)
        else:
            # Fall back to hierarchical detection with blog listing enhancement
            detector = HierarchicalStructureDetector()
            structure = detector.detect_hierarchical_structure(soup, url, max_articles)
        
        # Build organized output
        result = {
            'site': url,
            'page_title': structure.page_title,
            'page_description': structure.page_description,
            'navigation_structure': structure.navigation_structure,
            'platform_info': {
                'name': platform_info.name,
                'confidence': platform_info.confidence,
                'architecture': platform_info.architecture
            },
            'groups': []
        }
        
        for group in structure.topic_groups:
            group_data = {
                'type': group.group_type,
                'header': group.header_text,
                'anchor_id': group.anchor_id,
                'card_count': len(group.cards),
                'cards': []
            }
            
            for card in group.cards:
                card_data = {
                    'label': card.label,
                    'main_link': card.main_link,
                    'description': card.description,
                    'card_type': card.card_type,
                    'secondary_links': [
                        {'type': link.get('link_type', 'other'), 'url': link.get('url', ''), 'text': link.get('text', '')}
                        if isinstance(link, dict) else 
                        {'type': getattr(link, 'link_type', 'other'), 'url': getattr(link, 'url', ''), 'text': getattr(link, 'text', '')}
                        for link in card.secondary_links
                    ],
                    'metadata': card.metadata
                }
                group_data['cards'].append(card_data)
            
            result['groups'].append(group_data)
        
        return result
    
    def convert_to_standard_format(self, hierarchical_result: Dict) -> Dict:
        """Convert hierarchical result to standardized format"""
        standard_items = []
        site_url = hierarchical_result.get('site', '')
        
        # Extract items from all groups
        for group in hierarchical_result.get('groups', []):
            for card in group.get('cards', []):
                item = self._convert_card_to_item(card, hierarchical_result, site_url)
                if item:
                    standard_items.append(item)
        
        return {
            "site": site_url,
            "items": standard_items
        }
    
    def _convert_card_to_item(self, card: Dict, hierarchical_result: Dict, site_url: str) -> Optional[Dict]:
        """Convert a single card to standardized item format"""
        if not card.get('label'):
            return None
        
        # Determine content type based on platform and content patterns
        content_type = self._detect_content_type(card, hierarchical_result, site_url)
        
        # For blog articles, always try to fetch full content from the URL
        content = card.get('description', '')
        if card.get('main_link') and content_type in ['blog', 'article', 'post']:
            print(f"📄 Extracting full content from: {card['main_link']}")
            full_content = self._extract_content_from_url(card['main_link'])
            if full_content and len(full_content.strip()) > len(content.strip()):
                content = full_content
        elif not content and card.get('main_link'):
            # For non-blog content, only fetch if no description exists
            content = self._extract_content_from_url(card['main_link'])
        
        # Convert content to markdown if it's HTML
        if content:
            content = self._ensure_markdown_format(content)
        
        return {
            "title": card.get('label', '').strip(),
            "content": content,
            "content_type": content_type,
            "source_url": card.get('main_link', ''),
        }
    
    def _detect_content_type(self, card: Dict, hierarchical_result: Dict, site_url: str) -> str:
        """Detect the content type based on platform and content patterns"""
        platform_info = hierarchical_result.get('platform_info', {})
        platform_name = platform_info.get('name', '').lower()
        
        title = card.get('label', '').lower()
        description = card.get('description', '').lower()
        url = card.get('main_link', '').lower()
        
        # Platform-specific classifications
        if platform_name == 'substack':
            if any(word in title for word in ['newsletter', 'issue', 'digest']):
                return 'blog'
            return 'blog'  # Substack is primarily blog content
        
        elif platform_name == 'medium':
            return 'blog'  # Medium is primarily blog content
        
        elif platform_name == 'linkedin':
            return 'linkedin_post'
        
        elif platform_name == 'reddit':
            return 'reddit_comment'
        
        # Content pattern detection
        if any(word in title + description for word in ['podcast', 'episode', 'interview', 'transcript']):
            return 'podcast_transcript'
        
        elif any(word in title + description for word in ['call', 'meeting', 'transcript', 'recording']):
            return 'call_transcript'
        
        elif any(word in url for word in ['book', 'chapter', 'read']):
            return 'book'
        
        # Default to blog for most content
        return 'blog'
    
    def _extract_content_from_url(self, url: str) -> str:
        """Extract full content from a URL"""
        try:
            # Use the bot evasion system to fetch the page
            soup = self.bot_evasion.get_page(url)
            if not soup:
                return ""
            
            # Extract main content using multiple strategies
            content = self._extract_main_content(soup)
            
            # Convert to markdown and clean up
            if content:
                return self._ensure_markdown_format(content)
            
            return ""
        except Exception as e:
            print(f"⚠️ Error extracting content from {url}: {e}")
            return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from a page using multiple strategies"""
        # Strategy 1: Look for common article/post content selectors
        content_selectors = [
            'article', '.post-content', '.entry-content', '.content', 
            '.article-content', '.blog-content', 'main', '.main',
            '[role="main"]', '.post-body', '.entry', '.post'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Get the largest content block
                largest = max(elements, key=lambda x: len(x.get_text()))
                content_text = largest.get_text(separator='\n', strip=True)
                if len(content_text) > 200:  # Ensure substantial content
                    return str(largest)
        
        # Strategy 2: Look for the largest text block in the body
        if soup.body:
            # Remove navigation, header, footer, sidebar elements
            for tag in soup.body(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                tag.decompose()
            
            # Find all divs and get the one with most text
            divs = soup.body.find_all(['div', 'section', 'main'])
            if divs:
                largest_div = max(divs, key=lambda x: len(x.get_text()))
                content_text = largest_div.get_text(separator='\n', strip=True)
                if len(content_text) > 200:
                    return str(largest_div)
        
        # Strategy 3: Fallback to body content
        if soup.body:
            return str(soup.body)
        
        return ""
    
    def _ensure_markdown_format(self, content: str) -> str:
        """Ensure content is in markdown format"""
        if not content:
            return ""
        
        # If content contains HTML tags, convert to markdown
        if '<' in content and '>' in content:
            try:
                markdown_content = md(content, 
                                    heading_style="ATX",
                                    bullets="-",
                                    strong_em_style="**",
                                    strip=['a'])
                return self._clean_markdown(markdown_content)
            except:
                return content.strip()
        
        return content.strip()
    
    def _clean_markdown(self, markdown_content: str) -> str:
        """Clean up markdown content to make it more readable"""
        if not markdown_content:
            return ""
        
        # Fix common markdown issues
        # Remove excessive newlines but preserve paragraph breaks
        markdown_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown_content)
        
        # Remove leading/trailing whitespace from lines
        lines = []
        for line in markdown_content.split('\n'):
            cleaned_line = line.strip()
            lines.append(cleaned_line)
        
        markdown_content = '\n'.join(lines)
        
        # Remove excessive spaces
        markdown_content = re.sub(r' +', ' ', markdown_content)
        
        # Ensure proper spacing after headers
        markdown_content = re.sub(r'(#+[^\n]+)\n([^\n#])', r'\1\n\n\2', markdown_content)
        
        # Ensure proper spacing before lists
        markdown_content = re.sub(r'([^\n])\n([-*+])', r'\1\n\n\2', markdown_content)
        
        return markdown_content.strip()
    
    def _extract_platform_content(self, soup: BeautifulSoup, url: str, platform_info: PlatformInfo, max_articles: int = 20) -> 'HierarchicalStructure':
        """Extract content using platform-specific selectors"""
        # Get platform-specific selectors
        selectors = platform_info.content_selectors
        
        # Extract basic page info
        title_elem = soup.find('title')
        page_title = title_elem.get_text().strip() if title_elem else "Unknown Title"
        
        desc_elem = soup.find('meta', attrs={'name': 'description'})
        page_description = desc_elem.get('content', '').strip() if desc_elem else ""
        
        # Find posts using platform-specific selectors - try multiple approaches
        posts = []
        
        # Try primary selectors
        for selector in selectors['posts'].split(', '):
            found_posts = soup.select(selector.strip())
            posts.extend(found_posts)
            if len(posts) > 5:  # If we found some posts, break to avoid duplicates
                break
        
        # For Substack specifically, also try to find posts in common containers
        if platform_info.name == 'substack':
            # Look for links that go to /p/ (individual posts)
            post_links = soup.find_all('a', href=lambda x: x and '/p/' in x)
            for link in post_links:
                # Find the parent container that likely contains the full post info
                parent = link.find_parent(['div', 'article', 'section'])
                if parent and parent not in posts:
                    posts.append(parent)
        
        print(f"📋 Found {len(posts)} potential post elements")
        
        cards = []
        seen_urls = set()  # Avoid duplicates
        
        for post in posts[:30]:  # Increase limit for better coverage
            card = self._extract_platform_card(post, selectors, url)
            if card and card.label.strip() and card.main_link not in seen_urls:
                cards.append(card)
                seen_urls.add(card.main_link)
                if len(cards) >= 20:  # Reasonable limit
                    break
        
        print(f"✅ Extracted {len(cards)} unique blog posts")
        
        # Create a topic group for the posts
        if cards:
            group_type = f"{platform_info.name.title()} Posts"
            topic_group = TopicGroup(
                group_type=group_type,
                header_text=f"Latest {group_type}",
                anchor_id=None,
                cards=cards,
                group_metadata={}
            )
            
            return HierarchicalStructure(
                page_title=page_title,
                page_description=page_description,
                topic_groups=[topic_group],
                navigation_structure={},
                metadata={}
            )
        else:
            # Fall back to hierarchical detection
            detector = HierarchicalStructureDetector()
            return detector.detect_hierarchical_structure(soup, url)
    
    def _extract_platform_card(self, post_elem, selectors: Dict[str, str], base_url: str) -> Optional[CardInfo]:
        """Extract a card from a platform-specific post element"""
        # Extract title - try multiple approaches
        title = ""
        title_elem = None
        
        # Try the platform-specific selectors first
        for title_selector in selectors['title'].split(', '):
            title_elem = post_elem.select_one(title_selector.strip())
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # If no title found with selectors, look for any heading or link text
        if not title:
            # Look for any link that goes to /p/ (Substack post pattern)
            post_link = post_elem.find('a', href=lambda x: x and '/p/' in x)
            if post_link:
                title = post_link.get_text().strip()
            else:
                # Try any heading element
                for heading in post_elem.find_all(['h1', 'h2', 'h3', 'h4']):
                    title = heading.get_text().strip()
                    if title:
                        break
        
        if not title:
            return None
        
        # Extract main link
        main_link = ""
        
        # Look for Substack post link pattern first
        link_elem = post_elem.find('a', href=lambda x: x and '/p/' in x)
        if link_elem and link_elem.get('href'):
            main_link = urljoin(base_url, link_elem.get('href'))
        else:
            # Fallback to any link
            link_elem = post_elem.find('a')
            if link_elem and link_elem.get('href'):
                main_link = urljoin(base_url, link_elem.get('href'))
        
        # Extract content/description - try multiple selectors
        description = ""
        for content_selector in selectors['content'].split(', '):
            content_elem = post_elem.select_one(content_selector.strip())
            if content_elem:
                description = content_elem.get_text().strip()[:500]  # Limit length
                break
        
        # If no description found, try to get any text content (excluding title)
        if not description:
            all_text = post_elem.get_text().strip()
            # Remove the title from the text to get description
            if title in all_text:
                description = all_text.replace(title, '').strip()[:500]
            else:
                description = all_text[:500]
        
        # Extract metadata (author, date, interactions)
        metadata = {}
        secondary_links = []
        
        # Author
        author_elem = post_elem.select_one(selectors['author'])
        if author_elem:
            metadata['author'] = author_elem.get_text().strip()
            author_link = author_elem.find('a')
            if author_link and author_link.get('href'):
                secondary_links.append({
                    'link_type': 'author',
                    'url': urljoin(base_url, author_link.get('href')),
                    'text': metadata['author']
                })
        
        # Date
        date_elem = post_elem.select_one(selectors['date'])
        if date_elem:
            metadata['date'] = date_elem.get_text().strip()
        
        # Interaction elements
        interaction_elem = post_elem.select_one(selectors['interaction'])
        if interaction_elem:
            interactions = interaction_elem.get_text().strip()
            if interactions:
                metadata['interactions'] = interactions
        
        return CardInfo(
            label=title,
            main_link=main_link,
            description=description,
            card_type='post',
            secondary_links=secondary_links,
            metadata=metadata
        )


class HierarchicalScraper:
    """Main scraper class for hierarchical card-based structures"""
    
    def __init__(self):
        self.bot_evasion = BotEvasion()
        self.content_extractor = HierarchicalContentExtractor(self.bot_evasion)
    
    def scrape_hierarchical_site(self, url: str, max_additional_pages: int = 5, max_articles: int = 20) -> Dict:
        """Scrape a hierarchical site and return standardized format"""
        print(f"🧠 Starting hierarchical scrape: {url}")
        if max_articles != 20:
            print(f"📊 Max articles limit set to: {max_articles}")
        
        # Fetch main page
        soup = self.bot_evasion.get_page(url)
        if not soup:
            return {'error': 'Could not fetch the page'}
        
        # Extract hierarchical structure
        hierarchical_structure = self.content_extractor.extract_hierarchical_content(soup, url, max_articles)
        
        # Check if we got useful content, if not try alternatives
        # Special case: if we detected blog articles, don't try alternatives
        has_blog_articles = (hierarchical_structure.get('groups') and 
                           any(group.get('type') == 'Blog Articles' for group in hierarchical_structure.get('groups', [])))
        
        if (not has_blog_articles and 
            (not hierarchical_structure.get('groups') or 
             len(hierarchical_structure.get('groups', [])) == 0 or
             self._is_redirect_page(soup))):
            
            print("🔄 Main page seems to be a redirect or has no content, trying alternatives...")
            alternative_urls = self.bot_evasion.get_alternative_urls(url)
            
            for alt_url in alternative_urls:
                print(f"   Trying: {alt_url}")
                alt_soup = self.bot_evasion.get_page(alt_url)
                if alt_soup:
                    alt_structure = self.content_extractor.extract_hierarchical_content(alt_soup, alt_url, max_articles)
                    if (alt_structure.get('groups') and 
                        len(alt_structure.get('groups', [])) > 0 and
                        not self._is_redirect_page(alt_soup)):
                        print(f"✅ Found content at: {alt_url}")
                        hierarchical_structure = alt_structure
                        hierarchical_structure['original_url'] = url
                        hierarchical_structure['successful_url'] = alt_url
                        break
        
        # Convert to standardized format
        standard_result = self.content_extractor.convert_to_standard_format(hierarchical_structure)
        
        # Optionally scrape some linked pages for more content
        if max_additional_pages > 0:
            self._scrape_additional_content(standard_result, max_additional_pages)
        
        return standard_result
    
    def _is_redirect_page(self, soup):
        """Check if this appears to be a redirect or terms page"""
        if not soup:
            return True
            
        # Check for common redirect indicators
        redirect_indicators = [
            'terms of use', 'terms of service', 'privacy policy',
            'redirecting', 'please wait', 'loading',
            'terms-of-use', 'tos', 'legal'
        ]
        
        page_text = soup.get_text().lower()
        title = soup.find('title')
        title_text = title.get_text().lower() if title else ""
        
        for indicator in redirect_indicators:
            if indicator in page_text or indicator in title_text:
                return True
                
        return False
    
    def _scrape_additional_pages(self, structure: Dict, max_pages: int):
        """Scrape additional pages from the main structure"""
        pages_scraped = 0
        
        for group in structure.get('groups', []):
            if pages_scraped >= max_pages:
                break
                
            for card in group.get('cards', []):
                if pages_scraped >= max_pages:
                    break
                
                main_link = card.get('main_link', '')
                if main_link and main_link.startswith(('http', '/')):
                    print(f"📖 Scraping additional page: {card.get('label', 'Unknown')}")
                    
                    page_soup = self.bot_evasion.get_page(main_link)
                    if page_soup:
                        # Extract basic content from the page
                        page_content = self._extract_page_content(page_soup)
                        card['page_content'] = page_content
                        pages_scraped += 1
    
    def _extract_page_content(self, soup: BeautifulSoup) -> Dict:
        """Extract full content from a linked page and convert to expected format"""
        # Extract title
        title = ""
        title_selectors = [
            'h1', '.page-title', '.article-title', '.guide-title',
            '.post-title', 'title', '.main-heading'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                title = title_element.get_text(strip=True)
                break
        
        # Extract main content with priority order
        content_html = None
        content_selectors = [
            'main article',
            '.guide-content',
            '.interview-guide', 
            '.post-content',
            '.article-content',
            '.entry-content',
            '.blog-content',
            '.content-area',
            'main .content',
            'article',
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content_html = content_element
                break
        
        # Clean up content and convert to markdown
        if content_html:
            # Remove unwanted elements
            for element in content_html.find_all(['script', 'style', 'nav', 'header', 'footer', '.sidebar', '.advertisement']):
                element.decompose()
            
            # Convert to markdown
            try:
                from markdownify import markdownify
                content_markdown = markdownify(str(content_html), heading_style="ATX")
                
                # Clean up markdown
                content_markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', content_markdown)  # Remove excessive newlines
                content_markdown = re.sub(r'^\s+', '', content_markdown, flags=re.MULTILINE)  # Remove leading spaces
                content_markdown = content_markdown.strip()
            except ImportError:
                # Fallback if markdownify not available
                content_markdown = content_html.get_text(strip=True)
        else:
            # Fallback to body text
            body = soup.find('body')
            if body:
                # Remove unwanted elements from body
                for element in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    element.decompose()
                content_markdown = body.get_text(strip=True)
            else:
                content_markdown = ""
        
        return {
            'title': title,
            'content': content_markdown,
            'content_preview': content_markdown[:500] + "..." if len(content_markdown) > 500 else content_markdown
        }
    
    def _determine_content_type(self, url: str, content: str) -> str:
        """Determine content type based on URL patterns and content analysis"""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # Blog patterns
        if any(pattern in url_lower for pattern in ['/blog/', '/post/', '/article/']):
            return "blog"
        
        # Guide/tutorial patterns
        if any(pattern in url_lower for pattern in ['/guide/', '/tutorial/', '/learn/']):
            return "blog"  # Treat guides as blog content
        
        # Interview/questions patterns
        if any(pattern in url_lower for pattern in ['/interview', '/question']):
            return "other"  # Interview question sets
        
        # Analyze content for type hints
        if any(keyword in content_lower for keyword in ['podcast', 'transcript', 'episode']):
            return "podcast_transcript"
        
        if any(keyword in content_lower for keyword in ['linkedin', 'professional network']):
            return "linkedin_post"
        
        if any(keyword in content_lower for keyword in ['reddit', 'subreddit', 'upvote']):
            return "reddit_comment"
        
        if len(content) > 5000 and any(keyword in content_lower for keyword in ['chapter', 'book', 'author']):
            return "book"
        
        # Default to blog for substantial content, other for short content
        return "blog" if len(content) > 1000 else "other"
    
    def convert_to_expected_format(self, hierarchical_results: Dict) -> Dict:
        """Convert hierarchical results to expected output format"""
        items = []
        
        for group in hierarchical_results.get('groups', []):
            for card in group.get('cards', []):
                if 'page_content' in card and card['page_content'].get('content'):
                    content_type = self._determine_content_type(
                        card.get('main_link', ''), 
                        card['page_content'].get('content', '')
                    )
                    
                    item = {
                        "title": card['page_content'].get('title', card.get('label', '')),
                        "content": card['page_content'].get('content', ''),
                        "content_type": content_type,
                        "source_url": card.get('main_link', '')
                    }
                    items.append(item)
        
        return {
            "site": hierarchical_results.get('site', ''),
            "items": items
        }
    
    def _scrape_additional_content(self, standard_result: Dict, max_pages: int):
        """Scrape additional content from the main result's URLs"""
        pages_scraped = 0
        
        for item in standard_result.get('items', []):
            if pages_scraped >= max_pages:
                break
                
            source_url = item.get('source_url')
            if source_url and not item.get('content'):  # Only if we don't have content yet
                print(f"📄 Fetching full content from: {source_url}")
                
                soup = self.bot_evasion.get_page(source_url)
                if soup:
                    # Extract main content from the page
                    content = self._extract_main_page_content(soup)
                    if content:
                        item['content'] = self.content_extractor._ensure_markdown_format(content)
                        pages_scraped += 1
                        print(f"   ✅ Content extracted ({len(content)} chars)")
                    else:
                        print(f"   ⚠️ No substantial content found")
                else:
                    print(f"   ❌ Failed to fetch page")
    
    def _extract_main_page_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from a page for items"""
        # Try multiple content selectors for full article content
        content_selectors = [
            'article', 
            '.post-content', '.content', '.entry-content', 
            '.post-body', '.article-content', '.article-body',
            'main', '.main-content',
            '[role="main"]',
            '.available-content',  # Substack specific
            '.body'  # Substack specific
        ]
        
        content_html = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content_html = content_elem
                break
        
        if content_html:
            # Remove unwanted elements but preserve structure
            for unwanted in content_html.select('script, style, nav, footer, aside, .sidebar, .advertisement, .subscribe, .paywall'):
                unwanted.decompose()
            
            # Convert HTML to clean markdown
            try:
                # Convert to markdown preserving structure
                markdown_content = md(str(content_html), 
                                    heading_style="ATX",
                                    bullets="-",
                                    strong_em_style="**",
                                    strip=['a'])
                
                # Clean up the markdown
                markdown_content = self._clean_markdown(markdown_content)
                
                return markdown_content[:10000]  # Increase limit for full articles
                
            except Exception as e:
                print(f"   ⚠️ Markdown conversion failed: {e}")
                # Fallback to cleaned text
                return self._extract_clean_text(content_html)
        
        # Fallback: get text from body but filter out navigation/footer content
        body = soup.find('body')
        if body:
            # Remove common non-content elements
            for unwanted in body.select('script, style, nav, footer, aside, .sidebar, .navigation, .menu, .subscribe, .paywall'):
                unwanted.decompose()
            
            return self._extract_clean_text(body)[:10000]
        
        return ""
    
    def _clean_markdown(self, markdown_content: str) -> str:
        """Clean up markdown content to make it more readable"""
        if not markdown_content:
            return ""
        
        # Fix common markdown issues
        # Remove excessive newlines but preserve paragraph breaks
        markdown_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown_content)
        
        # Remove leading/trailing whitespace from lines
        lines = []
        for line in markdown_content.split('\n'):
            cleaned_line = line.strip()
            lines.append(cleaned_line)
        
        markdown_content = '\n'.join(lines)
        
        # Remove excessive spaces
        markdown_content = re.sub(r' +', ' ', markdown_content)
        
        # Ensure proper spacing after headers
        markdown_content = re.sub(r'(#+[^\n]+)\n([^\n#])', r'\1\n\n\2', markdown_content)
        
        # Ensure proper spacing before lists
        markdown_content = re.sub(r'([^\n])\n([-*+])', r'\1\n\n\2', markdown_content)
        
        return markdown_content.strip()
    
    def _extract_clean_text(self, element) -> str:
        """Extract clean, formatted text from HTML element"""
        if not element:
            return ""
        
        # Get text with some structure preservation
        text_parts = []
        
        for elem in element.descendants:
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text_parts.append(f"\n\n## {elem.get_text().strip()}\n")
            elif elem.name == 'p':
                text = elem.get_text().strip()
                if text:
                    text_parts.append(f"\n{text}\n")
            elif elem.name in ['li']:
                text = elem.get_text().strip()
                if text:
                    text_parts.append(f"\n- {text}")
            elif elem.name in ['br']:
                text_parts.append("\n")
            elif elem.name in ['strong', 'b']:
                text = elem.get_text().strip()
                if text:
                    text_parts.append(f"**{text}**")
            elif isinstance(elem, str):
                text = elem.strip()
                if text and len(text) > 3:  # Avoid short fragments
                    text_parts.append(text)
        
        content = ''.join(text_parts)
        
        # Clean up the result
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Fix excessive newlines
        content = re.sub(r' +', ' ', content)  # Fix excessive spaces
        
        return content.strip()


def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hierarchical_scraper.py <url> [max_additional_pages] [max_articles]")
        print("Example: python hierarchical_scraper.py https://interviewing.io/topics#companies 5 50")
        print("  max_additional_pages: number of additional pages to scrape for content (default: 0)")
        print("  max_articles: maximum articles to extract from blog listings (default: 20)")
        sys.exit(1)
    
    url = sys.argv[1]
    max_additional_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    max_articles = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    scraper = HierarchicalScraper()
    standard_results = scraper.scrape_hierarchical_site(url, max_additional_pages, max_articles)
    
    # Output standardized results
    print("\n" + "="*60)
    print("UNIVERSAL SCRAPER RESULTS:")
    print("="*60)
    standard_output = json.dumps(standard_results, indent=2, ensure_ascii=False)
    print(standard_output)
    
    # Save standardized results
    standard_filename = f"universal_results_{urlparse(url).netloc}_{int(time.time())}.json"
    with open(standard_filename, 'w', encoding='utf-8') as f:
        f.write(standard_output)
    print(f"\n💾 Results saved to: {standard_filename}")
    
    if standard_results.get('items'):
        print(f"\n✅ Successfully scraped {len(standard_results['items'])} items!")
    else:
        print("\n⚠️  No content was extracted. This might be because:")
        print("   - max_additional_pages was set to 0")
        print("   - The pages don't contain substantial content")
        print("   - The site blocks content scraping")
        print("\n💡 Try increasing max_additional_pages parameter for content extraction")


if __name__ == "__main__":
    main()