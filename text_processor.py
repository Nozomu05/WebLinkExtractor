import re
import nltk
from collections import Counter, defaultdict
from typing import List, Dict, Any
import math

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract key terms from text using TF-IDF-like approach
    """
    if not text:
        return []
    
    # Tokenize and clean words
    words = word_tokenize(text.lower())
    
    # Get English stopwords
    stop_words = set(stopwords.words('english'))
    
    # Add common web-specific stopwords
    stop_words.update(['said', 'say', 'says', 'one', 'two', 'also', 'would', 'could', 'get', 'go', 'come'])
    
    # Filter out stopwords, punctuation, and short words
    filtered_words = [
        word for word in words 
        if word.isalpha() and len(word) > 2 and word not in stop_words
    ]
    
    # Get POS tags to focus on nouns and adjectives
    pos_tags = pos_tag(filtered_words)
    important_words = [
        word for word, pos in pos_tags 
        if pos.startswith(('NN', 'JJ', 'VB'))  # Nouns, adjectives, verbs
    ]
    
    # Count word frequencies
    word_freq = Counter(important_words)
    
    # Return top keywords
    return [word for word, count in word_freq.most_common(top_n)]

def calculate_sentence_similarity(sent1: str, sent2: str) -> float:
    """
    Calculate similarity between two sentences based on shared keywords
    """
    if not sent1 or not sent2:
        return 0.0
    
    # Extract keywords from both sentences
    words1 = set(extract_keywords(sent1, top_n=20))
    words2 = set(extract_keywords(sent2, top_n=20))
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def group_sentences_by_similarity(sentences: List[str], threshold: float = 0.15) -> List[List[str]]:
    """
    Group sentences that are semantically similar
    """
    if not sentences:
        return []
    
    groups = []
    used_sentences = set()
    
    for i, sentence in enumerate(sentences):
        if i in used_sentences:
            continue
        
        # Start a new group with this sentence
        current_group = [sentence]
        used_sentences.add(i)
        
        # Find similar sentences
        for j, other_sentence in enumerate(sentences[i+1:], i+1):
            if j in used_sentences:
                continue
            
            similarity = calculate_sentence_similarity(sentence, other_sentence)
            if similarity >= threshold:
                current_group.append(other_sentence)
                used_sentences.add(j)
        
        groups.append(current_group)
    
    return groups

def generate_topic_title(sentences: List[str]) -> str:
    """
    Generate a descriptive title for a group of sentences
    """
    if not sentences:
        return "Untitled Topic"
    
    # Combine all sentences in the group
    combined_text = ' '.join(sentences)
    
    # Extract top keywords
    keywords = extract_keywords(combined_text, top_n=5)
    
    if not keywords:
        # Fallback: use first few words of the first sentence
        first_sentence = sentences[0]
        words = first_sentence.split()[:6]
        return ' '.join(words) + "..."
    
    # Create title from top keywords
    if len(keywords) >= 2:
        return f"{keywords[0].title()} and {keywords[1].title()}"
    else:
        return keywords[0].title()

def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into logical paragraphs
    """
    if not text:
        return []
    
    # Split by double newlines first
    paragraphs = re.split(r'\n\s*\n', text)
    
    # If no clear paragraph breaks, split by sentences and group
    if len(paragraphs) <= 1:
        sentences = sent_tokenize(text)
        if len(sentences) <= 3:
            return [text]  # Keep as single paragraph if very short
        
        # Group sentences into paragraphs (roughly 3-5 sentences each)
        paragraphs = []
        current_paragraph = []
        
        for sentence in sentences:
            current_paragraph.append(sentence)
            if len(current_paragraph) >= 4:  # Group every 4 sentences
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        # Add remaining sentences
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
    
    # Clean and filter paragraphs
    cleaned_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and len(para) > 50:  # Minimum paragraph length
            cleaned_paragraphs.append(para)
    
    return cleaned_paragraphs

def process_and_group_content(content: str) -> List[Dict[str, Any]]:
    """
    Process webpage content and group it into logical topics
    """
    if not content or len(content.strip()) < 100:
        return []
    
    try:
        # Split content into paragraphs
        paragraphs = split_into_paragraphs(content)
        
        if not paragraphs:
            return []
        
        # If we have few paragraphs, treat each as a separate topic
        if len(paragraphs) <= 3:
            groups = []
            for i, para in enumerate(paragraphs, 1):
                keywords = extract_keywords(para, top_n=10)
                title = generate_topic_title([para])
                groups.append({
                    'title': title,
                    'content': para,
                    'keywords': keywords
                })
            return groups
        
        # For longer content, group similar paragraphs
        sentence_groups = group_sentences_by_similarity(paragraphs, threshold=0.2)
        
        # Convert sentence groups to topic groups
        topic_groups = []
        for i, group in enumerate(sentence_groups):
            if not group:
                continue
            
            # Combine sentences in the group
            combined_content = '\n\n'.join(group)
            
            # Generate title and extract keywords
            title = generate_topic_title(group)
            keywords = extract_keywords(combined_content, top_n=10)
            
            topic_groups.append({
                'title': title,
                'content': combined_content,
                'keywords': keywords
            })
        
        # If we ended up with too many small groups, merge similar ones
        if len(topic_groups) > 6:
            topic_groups = merge_small_groups(topic_groups)
        
        # Sort groups by length (longer content first)
        topic_groups.sort(key=lambda x: len(x['content']), reverse=True)
        
        return topic_groups
        
    except Exception as e:
        # If processing fails, return the original content as a single group
        return [{
            'title': 'Main Content',
            'content': content,
            'keywords': extract_keywords(content, top_n=10)
        }]

def merge_small_groups(groups: List[Dict[str, Any]], min_size: int = 200) -> List[Dict[str, Any]]:
    """
    Merge small topic groups with similar ones
    """
    if not groups:
        return []
    
    merged_groups = []
    small_groups = []
    
    # Separate small and large groups
    for group in groups:
        if len(group['content']) < min_size:
            small_groups.append(group)
        else:
            merged_groups.append(group)
    
    # Try to merge small groups with large ones based on keyword similarity
    for small_group in small_groups:
        best_match = None
        best_similarity = 0
        
        for large_group in merged_groups:
            # Calculate keyword similarity
            small_keywords = set(small_group['keywords'][:5])
            large_keywords = set(large_group['keywords'][:5])
            
            if small_keywords and large_keywords:
                similarity = len(small_keywords.intersection(large_keywords)) / len(small_keywords.union(large_keywords))
                if similarity > best_similarity and similarity > 0.2:
                    best_similarity = similarity
                    best_match = large_group
        
        if best_match:
            # Merge with the best matching group
            best_match['content'] += '\n\n' + small_group['content']
            # Update keywords
            combined_keywords = list(set(best_match['keywords'] + small_group['keywords']))
            best_match['keywords'] = combined_keywords[:10]
        else:
            # Keep as separate group if no good match found
            merged_groups.append(small_group)
    
    return merged_groups
