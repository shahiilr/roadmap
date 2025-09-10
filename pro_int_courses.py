#!/usr/bin/env python3
"""
Professional AI Course Recommender & Learning Roadmap Generator
===============================================================

Enhanced version with professional roadmap visualization
"""

import google.generativeai as genai
import json
import time
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np
from typing import List, Dict, Optional
import textwrap
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Load API Keys
def load_api_keys() -> List[str]:
    api_keys = []
    key1 = os.getenv('GEMINI_API_KEY_1')
    if key1:
        api_keys.append(key1)
        print("✅ Primary API key loaded")
    
    key2 = os.getenv('GEMINI_API_KEY_2')
    if key2:
        api_keys.append(key2)
        print("✅ Secondary API key loaded")
    
    if not api_keys:
        print("⚠️  No API keys found!")
        print("   To use this application, you need Google Gemini API keys.")
        print("   Get them from: https://makersuite.google.com/app/apikey")
        print("   Then create a .env file with:")
        print("   GEMINI_API_KEY_1=your_key_here")
        print("   GEMINI_API_KEY_2=your_second_key_here")
        return []
    
    print(f"🔑 Loaded {len(api_keys)} API key(s) for Gemini AI")
    return api_keys

API_KEYS = load_api_keys()

class ProfessionalAIClient:
    """Enhanced AI client for course and roadmap generation"""
    
    def __init__(self, api_keys: List[str]):
        if not api_keys:
            raise ValueError("No API keys provided. Please set up your Gemini API keys in .env file.")
        self.api_keys = api_keys
        self.current_key_index = 0
        self.max_retries = 3
        self.retry_delay = 2.0
    
    def _get_next_api_key(self) -> str:
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def generate_content(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                api_key = self._get_next_api_key()
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"⚠️  API call failed (attempt {attempt + 1}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    raise e
    
    def recommend_courses(self, interests: str, skills: str = "", goals: str = "") -> List[Dict]:
        """Generate course recommendations"""
        print("🤖 Generating AI course recommendations...")
        
        prompt = f"""
        Generate personalized course recommendations for:
        - Interests: {interests}
        - Current Skills: {skills or 'Not specified'}
        - Career Goals: {goals or 'Not specified'}

        Generate EXACTLY 8 high-quality courses with the following distribution:
        - 3 Beginner level courses
        - 3 Intermediate level courses  
        - 2 Advanced level courses

        Return as JSON:
        {{
            "courses": [
                {{
                    "title": "Specific course title",
                    "platform": "Coursera/Udemy/edX/LinkedIn Learning/etc",
                    "instructor": "Instructor name",
                    "duration": "Duration (e.g., '8 weeks', '40 hours')",
                    "difficulty": "Beginner/Intermediate/Advanced",
                    "rating": "Rating (4.0-5.0)",
                    "price": "Price (Free, $49/month, $99, etc.)",
                    "description": "2-sentence description",
                    "skills_gained": ["skill1", "skill2", "skill3"],
                    "url": "Course URL",
                    "level": "beginner/intermediate/advanced",
                    "certification": "Yes/No"
                }}
            ]
        }}

        Return ONLY the JSON object.
        """
        
        try:
            response_text = self.generate_content(prompt)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                return data.get('courses', [])
        except Exception as e:
            print(f"❌ Course generation error: {e}")
        
        return []
    
    def generate_roadmap(self, subject: str) -> Dict:
        """Generate learning roadmap"""
        print(f"🗺️  Generating learning roadmap for: {subject}")
        
        prompt = f"""
        Create a comprehensive learning roadmap for: {subject}

        Generate exactly 8 progressive learning steps. Return as JSON:
        {{
            "subject": "{subject}",
            "overview": "2-sentence overview of the learning journey",
            "total_duration": "Total estimated time (e.g., '6-12 months')",
            "prerequisites": ["prerequisite1", "prerequisite2"],
            "learning_path": [
                {{
                    "step": 1,
                    "title": "Step title",
                    "description": "What will be learned",
                    "duration": "2-4 weeks",
                    "difficulty": "Beginner/Intermediate/Advanced",
                    "topics": ["topic1", "topic2", "topic3"],
                    "milestone": "What you'll achieve"
                }}
            ],
            "career_outcomes": ["Job role 1", "Job role 2", "Job role 3"],
            "certifications": ["Certification 1", "Certification 2"],
            "salary_range": "Expected salary range",
            "industry_demand": "Market demand information"
        }}

        Ensure 8 steps with logical progression. Return ONLY JSON.
        """
        
        try:
            response_text = self.generate_content(prompt)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            print(f"❌ Roadmap generation error: {e}")
        
        # Fallback roadmap
        return {
            "subject": subject,
            "overview": f"A comprehensive learning path for {subject} covering fundamental to advanced concepts.",
            "total_duration": "6-12 months",
            "prerequisites": ["Basic computer literacy"],
            "learning_path": [
                {"step": i+1, "title": f"Step {i+1}: {['Foundations', 'Core Concepts', 'Practical Skills', 'Intermediate Topics', 'Advanced Techniques', 'Specialization', 'Expert Level', 'Mastery'][i]}", 
                 "description": f"Learn {subject} concepts at step {i+1}", "duration": "2-4 weeks", 
                 "difficulty": ["Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"][i],
                 "topics": [f"Topic {j+1}" for j in range(3)], "milestone": f"Complete step {i+1} objectives"}
                for i in range(8)
            ],
            "career_outcomes": [f"{subject} Specialist", f"{subject} Expert", f"{subject} Consultant"],
            "certifications": ["Professional certification programs available"],
            "salary_range": "Varies by location and experience",
            "industry_demand": "Growing demand in various industries"
        }

class ProfessionalRoadmapVisualizer:
    """Professional roadmap visualization with modern design"""
    
    def __init__(self):
        # Modern color palette
        self.colors = {
            'primary': '#2C3E50',      # Dark blue-gray
            'secondary': '#3498DB',     # Bright blue
            'accent': '#E74C3C',        # Red
            'success': '#27AE60',       # Green
            'warning': '#F39C12',       # Orange
            'background': '#FFFFFF',    # White
            'light_gray': '#F8F9FA',    # Light gray
            'medium_gray': '#BDC3C7',   # Medium gray
            'dark_gray': '#34495E',     # Dark gray
        }
        
        # Difficulty level colors
        self.difficulty_colors = {
            'beginner': self.colors['success'],      # Green
            'intermediate': self.colors['warning'],  # Orange  
            'advanced': self.colors['accent']        # Red
        }
        
        # Typography settings
        self.fonts = {
            'title': {'size': 24, 'weight': 'bold'},
            'subtitle': {'size': 14, 'weight': 'normal'},
            'heading': {'size': 12, 'weight': 'bold'},
            'body': {'size': 10, 'weight': 'normal'},
            'small': {'size': 8, 'weight': 'normal'},
        }
    
    def create_roadmap(self, roadmap_data: Dict, courses: List[Dict] = None) -> str:
        """Create clean roadmap visualization with only 8 learning steps"""
        subject = roadmap_data.get('subject', 'Learning Path')
        safe_filename = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_').lower()
        image_path = f"professional_roadmap_{safe_filename}.png"
        
        # Create figure with 50% increased horizontal length
        fig = plt.figure(figsize=(30, 16), dpi=300)  # Increased from 20 to 30 (50% increase)
        fig.patch.set_facecolor(self.colors['background'])
        
        # Create main axis with expanded horizontal space
        ax = fig.add_subplot(111)
        ax.set_xlim(0, 30)  # Increased from 20 to 30 (50% increase)
        ax.set_ylim(0, 16)
        ax.axis('off')
        
        # Draw only the essential components
        self._draw_header(ax, subject, roadmap_data.get('overview', ''))
        self._draw_timeline_only(ax, roadmap_data.get('learning_path', []))
        
        # Save with perfect settings to ensure complete visibility
        plt.tight_layout()
        plt.subplots_adjust(top=0.995, bottom=0.005, left=0.005, right=0.995)
        plt.savefig(image_path, dpi=300, bbox_inches=None,  # Don't use tight to prevent cutting
                   facecolor=self.colors['background'], edgecolor='none',
                   pad_inches=0)  # No extra padding to prevent size changes
        plt.close()
        
        print(f"✅ Clean 8-step roadmap saved: {image_path}")
        return image_path
    
    def _draw_header(self, ax, subject: str, overview: str):
        """Draw header with guaranteed full visibility - centered for wider layout"""
        # Header background - repositioned for wider 30-unit layout
        header_rect = FancyBboxPatch((3.5, 14.5), 23, 1.3,  # Centered in 30-unit width
                                    boxstyle="round,pad=0.2",
                                    facecolor='#B8C332',  # Yellow-green
                                    edgecolor='none', alpha=0.95)
        ax.add_patch(header_rect)
        
        # Title - centered at x=15 for 30-unit width
        ax.text(15, 15.4, f"🎯 {subject.upper()} LEARNING ROADMAP", 
                ha='center', va='center', color='white',
                fontsize=24, fontweight='bold', fontfamily='sans-serif')
        
        # Subtitle - centered at x=15 for 30-unit width
        ax.text(15, 14.8, "8-STEP LEARNING TIMELINE", 
                ha='center', va='center', color='white',
                fontsize=18, fontweight='bold', fontfamily='sans-serif', alpha=0.9)
    
    def _draw_timeline(self, ax, learning_path: List[Dict]):
        """Draw curved road timeline with proper alignment"""
        if not learning_path:
            return
        
        # Limit to 8 steps
        steps = learning_path[:8]
        
        # Timeline configuration - better centered positioning
        timeline_y = 10.5
        start_x = 2
        end_x = 22
        
        # Create curved road path
        self._draw_curved_road(ax, start_x, end_x, timeline_y)
        
        # Draw steps along the curved path with better spacing
        for i, step in enumerate(steps):
            # Calculate position along curved path
            progress = i / max(1, len(steps) - 1) if len(steps) > 1 else 0.5
            x = start_x + progress * (end_x - start_x)
            
            # Create wave effect for y position - more pronounced
            wave_amplitude = 2.0
            wave_y = timeline_y + wave_amplitude * np.sin(progress * np.pi * 2.5)
            
            self._draw_step(ax, step, x, wave_y, i + 1)
    
    def _draw_timeline_only(self, ax, learning_path: List[Dict]):
        """Draw perfect timeline with optimal spacing and layout"""
        if not learning_path:
            return
        
        # Limit to exactly 8 steps
        steps = learning_path[:8]
        
        # Timeline configuration - expanded for 50% longer horizontal layout
        timeline_y = 10
        start_x = 3     # Increased start margin for better positioning
        end_x = 27      # Expanded end point for 50% longer road (was 18, now 27)
        
        # Create smooth wavy road and get curve data
        road_x, road_y = self._draw_curved_road_clean(ax, start_x, end_x, timeline_y)
        
        # Calculate step positions along the actual road curve with perfect distribution
        step_positions = []
        for i in range(len(steps)):
            # Calculate position index along road curve
            progress = i / max(1, len(steps) - 1) if len(steps) > 1 else 0.5
            road_index = int(progress * (len(road_x) - 1))
            
            # Get actual position from road curve
            step_x = road_x[road_index]
            step_y = road_y[road_index]
            step_positions.append((step_x, step_y))
        
        # Draw steps with perfect spacing and alignment - NO HEADER OVERLAP
        # Improved distribution across 50% longer road
        used_positions = []
        header_zone_max = 14.0  # Absolute maximum Y to avoid header overlap
        
        for i, (step, (road_x_pos, road_y_pos)) in enumerate(zip(steps, step_positions)):
            # Safe card positioning - prevent header overlap with improved spacing
            card_offset = 3.0  # Optimized distance from road for longer layout
            
            # Improved alternating pattern for better visual balance on longer road
            if i % 2 == 0:
                card_y = road_y_pos + card_offset  # Above road
                # CRITICAL: Ensure card never enters header zone
                card_y = min(card_y, header_zone_max - 1.0)  # Keep 1.0 unit safety margin from header
            else:
                card_y = road_y_pos - card_offset  # Below road
            
            # Enhanced spacing for longer road layout
            min_distance = 5.5  # Increased minimum distance for better spacing on longer road
            for used_x, used_y in used_positions:
                distance = np.sqrt((road_x_pos - used_x)**2 + (card_y - used_y)**2)
                if distance < min_distance:
                    # Adjust position for perfect layout
                    if card_y > road_y_pos:  # Card is above road
                        adjusted_y = max(used_y + min_distance, card_y)
                        # CRITICAL: Double-check header zone protection
                        card_y = min(adjusted_y, header_zone_max - 1.0)
                    else:  # Card is below road
                        card_y = min(used_y - min_distance, card_y)
            
            # Store position for perfect spacing calculations
            used_positions.append((road_x_pos, card_y))
            
            # Draw the step with perfect alignment - no header overlap
            self._draw_step_clean(ax, step, road_x_pos, road_y_pos, card_y, i + 1)
    
    def _draw_curved_road_clean(self, ax, start_x: float, end_x: float, center_y: float):
        """Draw perfect wavy road with professional appearance"""
        # Create ultra-smooth wavy path for perfect appearance
        x_points = np.linspace(start_x, end_x, 600)
        
        # Create perfect wavy pattern with optimal curves
        progress = (x_points - start_x) / (end_x - start_x)
        
        # Perfect sine wave for smooth, professional appearance
        wave_amplitude = 1.8
        y_points = center_y + wave_amplitude * np.sin(progress * np.pi * 2.8)
        
        # Draw perfect road surface with professional appearance
        road_width = 1.2
        
        # Create ultra-smooth road surface with gradient effect
        ax.plot(x_points, y_points, color='#5D6D7E', linewidth=road_width*50, 
                alpha=0.95, solid_capstyle='round', zorder=2)
        
        # Add road texture with multiple layers for depth
        ax.plot(x_points, y_points, color='#4A5568', linewidth=road_width*45, 
                alpha=0.7, solid_capstyle='round', zorder=2)
        
        # Draw perfect road edges with professional definition
        edge_offset = road_width/2 + 0.08
        
        # Top edge with perfect smoothness
        top_y = y_points + edge_offset
        ax.plot(x_points, top_y, color='#2D3748', linewidth=4, 
                alpha=0.9, solid_capstyle='round', zorder=3)
        
        # Bottom edge with perfect smoothness
        bottom_y = y_points - edge_offset
        ax.plot(x_points, bottom_y, color='#2D3748', linewidth=4, 
                alpha=0.9, solid_capstyle='round', zorder=3)
        
        # Draw perfect center line dashes with professional spacing
        dash_interval = 30
        dash_length = 18
        for i in range(0, len(x_points), dash_interval):
            if i + dash_length < len(x_points):
                # Draw bright, professional center dashes
                start_idx = i
                end_idx = min(i + dash_length, len(x_points) - 1)
                
                ax.plot([x_points[start_idx], x_points[end_idx]], 
                       [y_points[start_idx], y_points[end_idx]], 
                       color='#F59E0B', linewidth=8, alpha=0.95,
                       solid_capstyle='round', zorder=4)
        
        return x_points, y_points
    
    def _draw_step_clean(self, ax, step: Dict, road_x: float, road_y: float, card_y: float, step_num: int):
        """Draw step with proper alignment and no overlapping"""
        # Step colors - vibrant and distinct
        step_colors = [
            '#E91E63',  # Pink
            '#009688',  # Teal  
            '#9C27B0',  # Purple
            '#FF9800',  # Orange
            '#2196F3',  # Blue
            '#4CAF50',  # Green
            '#F44336',  # Red
            '#795548'   # Brown
        ]
        
        step_color = step_colors[(step_num - 1) % len(step_colors)]
        
        # Draw location pin marker on the road
        pin_radius = 0.4
        pin_circle = Circle((road_x, road_y), pin_radius, 
                           facecolor=step_color, edgecolor='white', 
                           linewidth=3, zorder=10)
        ax.add_patch(pin_circle)
        
        # Step number - bold and clear
        ax.text(road_x, road_y, str(step_num), ha='center', va='center', 
                color='white', fontsize=16, 
                fontweight='bold', fontfamily='sans-serif', zorder=11)
        
        # Draw step card at calculated position
        self._draw_step_card_clean(ax, step, road_x, card_y, step_color, step_num)
        
        # Clean connection line from road to card
        line_start_y = road_y + pin_radius if card_y > road_y else road_y - pin_radius
        line_end_y = card_y - 0.7 if card_y > road_y else card_y + 0.7
        
        ax.plot([road_x, road_x], [line_start_y, line_end_y], 
               color=step_color, linewidth=3, alpha=0.8, zorder=5)
    
    def _draw_step_card_clean(self, ax, step: Dict, x: float, y: float, color: str, step_num: int):
        """Draw perfect step card with professional design - NO HEADER OVERLAP - Optimized for wider layout"""
        card_width = 5.0   # Slightly wider cards for better proportion on longer road
        card_height = 1.8  # Slightly taller for better readability
        
        # Ensure perfect positioning within boundaries
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # CRITICAL: Header zone protection
        header_zone_max = 14.0  # Absolute maximum Y to avoid header overlap
        safe_card_max_y = header_zone_max - card_height/2 - 0.2  # Safety margin
        
        # Perfect boundary adjustments with header protection - optimized for 30-unit width
        margin = 0.5  # Increased margin for wider layout
        if x - card_width/2 < x_min + margin:
            x = x_min + card_width/2 + margin
        elif x + card_width/2 > x_max - margin:
            x = x_max - card_width/2 - margin
            
        if y - card_height/2 < y_min + margin:
            y = y_min + card_height/2 + margin
        elif y + card_height/2 > y_max - margin:
            y = y_max - card_height/2 - margin
            
        # CRITICAL: Enforce header zone protection - card cannot enter header area
        if y > safe_card_max_y:
            y = safe_card_max_y
        
        # Perfect card shadow with professional depth
        shadow = FancyBboxPatch((x - card_width/2 + 0.1, y - card_height/2 - 0.1), 
                               card_width, card_height,
                               boxstyle="round,pad=0.15", 
                               facecolor='#1A202C', alpha=0.3, zorder=6)
        ax.add_patch(shadow)
        
        # Perfect main card background with professional styling
        card = FancyBboxPatch((x - card_width/2, y - card_height/2), 
                             card_width, card_height,
                             boxstyle="round,pad=0.15", 
                             facecolor='white', 
                             edgecolor=color, linewidth=3.5,
                             alpha=0.98, zorder=7)
        ax.add_patch(card)
        
        # Perfect step content - ONLY MAIN CONCEPT with larger text
        title = step.get('title', f'Step {step_num}')
        duration = step.get('duration', 'Duration')
        difficulty = step.get('difficulty', 'Beginner').title()
        
        # LARGER title formatting - focus on main concept only
        wrapped_title = textwrap.wrap(title, 25)  # Slightly shorter wrap for bigger text
        main_title = wrapped_title[0] if wrapped_title else title
        
        # MUCH LARGER main title - primary focus
        ax.text(x, y + 0.3, main_title, ha='center', va='center',
                fontsize=18, fontweight='bold', fontfamily='sans-serif',  # Increased from 14 to 18
                color=self.colors['primary'], zorder=8)
        
        # LARGER second line if needed
        if len(wrapped_title) > 1:
            ax.text(x, y - 0.1, wrapped_title[1], ha='center', va='center',
                    fontsize=16, fontweight='bold', fontfamily='sans-serif',  # Increased from 13 to 16
                    color=self.colors['primary'], zorder=8)
        
        # LARGER bottom information - only essential details
        bottom_y = y - 0.45
        ax.text(x - 1.2, bottom_y, f"⏱️ {duration}", ha='center', va='center',
                fontsize=12, fontweight='bold', fontfamily='sans-serif',  # Increased from 10 to 12
                color=color, zorder=8)
        ax.text(x + 1.2, bottom_y, f"📊 {difficulty}", ha='center', va='center',
                fontsize=12, fontweight='bold', fontfamily='sans-serif',  # Increased from 10 to 12
                color=color, zorder=8)
    
    def _draw_minimal_footer(self, ax, roadmap_data: Dict):
        """Draw minimal footer with essential info only"""
        # Small footer for essential info
        footer_rect = FancyBboxPatch((1, 0.2), 18, 1.5,
                                    boxstyle="round,pad=0.1",
                                    facecolor=self.colors['light_gray'],
                                    edgecolor=self.colors['medium_gray'],
                                    linewidth=1.5, alpha=0.9)
        ax.add_patch(footer_rect)
        
        # Duration info - left
        total_duration = roadmap_data.get('total_duration', 'Not specified')
        ax.text(5, 1.2, f"⏳ Total Duration: {total_duration}", 
                ha='center', va='center',
                fontsize=12, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['primary'])
        
        # Prerequisites - center
        prerequisites = roadmap_data.get('prerequisites', [])
        if prerequisites:
            prereq_text = f"📋 Prerequisites: {', '.join(prerequisites[:2])}"
            if len(prerequisites) > 2:
                prereq_text += "..."
            ax.text(10, 1.2, prereq_text, 
                    ha='center', va='center',
                    fontsize=11, fontfamily='sans-serif',
                    color=self.colors['dark_gray'])
        
        # Career outcome - right
        career_outcomes = roadmap_data.get('career_outcomes', [])
        if career_outcomes:
            ax.text(15, 1.2, f"🚀 Career: {career_outcomes[0]}", 
                    ha='center', va='center',
                    fontsize=12, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['success'])
        
        # Simple branding
        ax.text(10, 0.5, "8-Step AI Learning Roadmap", 
                ha='center', va='center',
                fontsize=10, fontfamily='sans-serif',
                color=self.colors['medium_gray'],
                style='italic')
    
    def _draw_curved_road(self, ax, start_x: float, end_x: float, center_y: float):
        """Draw smooth curved road path"""
        # Create much smoother curved path with more points
        x_points = np.linspace(start_x, end_x, 500)  # More points for smoother curve
        wave_amplitude = 1.8
        y_points = center_y + wave_amplitude * np.sin((x_points - start_x) / (end_x - start_x) * np.pi * 2.5)
        
        # Draw road background (wider and smoother)
        for i in range(len(x_points) - 1):
            # Create smooth road segments
            road_width = 0.5
            segment_length = np.sqrt((x_points[i+1] - x_points[i])**2 + (y_points[i+1] - y_points[i])**2)
            
            # Road segment
            road_segment = Circle((x_points[i], y_points[i]), road_width/2,
                                facecolor='#34495E', edgecolor='none', alpha=0.9)
            ax.add_patch(road_segment)
        
        # Draw smooth dashed line in the middle
        dash_x = x_points[::15]  # Every 15th point for smoother dashes
        dash_y = y_points[::15]
        
        for i in range(0, len(dash_x) - 2, 3):  # Longer dashes
            ax.plot([dash_x[i], dash_x[i+2]], 
                   [dash_y[i], dash_y[i+2]], 
                   color='white', linewidth=3, linestyle='-', alpha=0.9)
    
    def _draw_step(self, ax, step: Dict, x: float, y: float, step_num: int):
        """Draw individual timeline step with proper alignment"""
        # Color scheme similar to sample image
        step_colors = [
            '#E91E63',  # Pink (like step 1 in sample)
            '#009688',  # Teal (like step 2 in sample)  
            '#9C27B0',  # Purple (like step 3 in sample)
            '#FF9800',  # Orange (like step 4 in sample)
            '#2196F3',  # Blue (like step 5 in sample)
            '#4CAF50',  # Green
            '#F44336',  # Red
            '#795548'   # Brown
        ]
        
        # Get color for this step
        step_color = step_colors[(step_num - 1) % len(step_colors)]
        
        # Draw location pin/marker - larger and more visible
        pin_height = 1.0
        pin_width = 0.8
        
        # Pin body (circle)
        pin_circle = Circle((x, y + pin_height/3), pin_width/2, 
                           facecolor=step_color, edgecolor='white', 
                           linewidth=3, zorder=10)
        ax.add_patch(pin_circle)
        
        # Pin point (triangle) - better positioned
        triangle_points = np.array([[x, y - 0.1], 
                                   [x - pin_width/3, y + pin_height/2], 
                                   [x + pin_width/3, y + pin_height/2]])
        triangle = patches.Polygon(triangle_points, facecolor=step_color, 
                                 edgecolor='white', linewidth=3, zorder=10)
        ax.add_patch(triangle)
        
        # Step number in white - larger font
        ax.text(x, y + pin_height/3, str(step_num), ha='center', va='center', 
                color='white', fontsize=14, 
                fontweight='bold', zorder=11)
        
        # Step information card with better positioning
        if step_num % 2 == 1:
            card_y = y + 3.0  # Above the road
        else:
            card_y = y - 3.0  # Below the road
            
        self._draw_step_card(ax, step, x, card_y, step_color)
        
        # Connection line from pin to card - cleaner lines
        if step_num % 2 == 1:
            ax.plot([x, x], [y + pin_height/2 + 0.2, card_y - 0.8], 
                   color=step_color, linewidth=3, alpha=0.8)
        else:
            ax.plot([x, x], [y - 0.3, card_y + 0.8], 
                   color=step_color, linewidth=3, alpha=0.8)
    
    def _draw_step_card(self, ax, step: Dict, x: float, y: float, color: str):
        """Draw step information card with improved fonts and alignment"""
        card_width = 3.8
        card_height = 1.8
        
        # Card background with rounded corners and better shadow
        shadow = FancyBboxPatch((x - card_width/2 + 0.08, y - card_height/2 - 0.08), 
                               card_width, card_height,
                               boxstyle="round,pad=0.2", 
                               facecolor='gray', alpha=0.3, zorder=1)
        ax.add_patch(shadow)
        
        card = FancyBboxPatch((x - card_width/2, y - card_height/2), 
                             card_width, card_height,
                             boxstyle="round,pad=0.2", 
                             facecolor='white', 
                             edgecolor=color, linewidth=3,
                             alpha=0.98, zorder=2)
        ax.add_patch(card)
        
        # Card content with improved fonts
        title = step.get('title', 'Step Title')
        duration = step.get('duration', 'Duration')
        difficulty = step.get('difficulty', 'Beginner').title()
        
        # Main title - larger, bold font
        wrapped_title = textwrap.wrap(title, 25)
        main_title = wrapped_title[0] if wrapped_title else title
        ax.text(x, y + 0.5, main_title, ha='center', va='center',
                fontsize=13, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['primary'], zorder=3)
        
        # Second line of title if needed
        if len(wrapped_title) > 1:
            ax.text(x, y + 0.2, wrapped_title[1], ha='center', va='center',
                    fontsize=11, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['primary'], zorder=3)
        
        # Description text - better readability
        description = step.get('description', '')
        if len(description) > 70:
            description = description[:70] + "..."
        wrapped_desc = textwrap.wrap(description, 32)
        
        desc_y = y - 0.1 if len(wrapped_title) > 1 else y + 0.1
        for i, desc_line in enumerate(wrapped_desc[:2]):
            ax.text(x, desc_y - i*0.25, desc_line, ha='center', va='center',
                    fontsize=10, fontfamily='sans-serif',
                    color=self.colors['dark_gray'], zorder=3)
        
        # Duration and difficulty - clearer formatting
        bottom_y = y - 0.6
        ax.text(x, bottom_y, f"⏱️ {duration}", ha='center', va='center',
                fontsize=9, fontweight='bold', fontfamily='sans-serif',
                color=color, zorder=3)
        ax.text(x, bottom_y - 0.2, f"📊 {difficulty}", ha='center', va='center',
                fontsize=9, fontweight='bold', fontfamily='sans-serif',
                color=color, zorder=3)
    
    def _draw_sidebar(self, ax, roadmap_data: Dict):
        """Draw information sidebar with improved fonts and alignment"""
        # Sidebar background - better positioned
        sidebar_rect = FancyBboxPatch((0.5, 5.5), 4.5, 8,
                                     boxstyle="round,pad=0.2",
                                     facecolor=self.colors['light_gray'],
                                     edgecolor=self.colors['medium_gray'],
                                     linewidth=2, alpha=0.95)
        ax.add_patch(sidebar_rect)
        
        # Title - larger, more prominent
        ax.text(2.75, 13, "📋 LEARNING INFO", 
                ha='center', va='center', 
                fontsize=16, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['primary'])
        
        y_pos = 12.2
        
        # Prerequisites with improved formatting
        prerequisites = roadmap_data.get('prerequisites', [])
        if prerequisites:
            ax.text(2.75, y_pos, "🔹 Prerequisites:", 
                    ha='center', va='center', 
                    fontsize=12, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['dark_gray'])
            y_pos -= 0.5
            
            for prereq in prerequisites[:3]:
                wrapped_prereq = textwrap.wrap(f"• {prereq}", 30)
                ax.text(0.8, y_pos, wrapped_prereq[0], 
                        ha='left', va='center', 
                        fontsize=10, fontfamily='sans-serif',
                        color=self.colors['dark_gray'])
                y_pos -= 0.35
        
        y_pos -= 0.4
        
        # Duration - better formatted
        total_duration = roadmap_data.get('total_duration', 'Not specified')
        ax.text(2.75, y_pos, "⏳ Duration:", 
                ha='center', va='center', 
                fontsize=12, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['dark_gray'])
        y_pos -= 0.4
        ax.text(2.75, y_pos, total_duration, 
                ha='center', va='center', 
                fontsize=11, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['secondary'])
        
        y_pos -= 0.7
        
        # Difficulty legend with better styling
        ax.text(2.75, y_pos, "📊 Difficulty Levels:", 
                ha='center', va='center', 
                fontsize=12, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['dark_gray'])
        y_pos -= 0.5
        
        levels = [
            ('🟢 Beginner', self.difficulty_colors['beginner']),
            ('🟡 Intermediate', self.difficulty_colors['intermediate']),
            ('🔴 Advanced', self.difficulty_colors['advanced'])
        ]
        
        for level, color in levels:
            ax.text(2.75, y_pos, level, ha='center', va='center',
                    fontsize=11, fontweight='bold', fontfamily='sans-serif',
                    color=color)
            y_pos -= 0.35
    
    def _draw_courses(self, ax, courses: List[Dict]):
        """Draw course recommendations with perfect grid alignment and better fonts"""
        if not courses:
            return
        
        # Title - larger, more prominent
        ax.text(15, 14.2, "📚 RECOMMENDED COURSES", 
                ha='center', va='center',
                fontsize=18, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['primary'])
        
        # Course grid layout - perfectly aligned 2x4 grid
        grid_start_x = 6
        grid_start_y = 13.2
        course_width = 4.5
        course_height = 1.5
        cols = 4
        spacing_x = 0.4
        spacing_y = 0.6
        
        # Show top 8 courses in a perfect 2x4 grid
        for i, course in enumerate(courses[:8]):
            row = i // cols
            col = i % cols
            
            x = grid_start_x + col * (course_width + spacing_x)
            y = grid_start_y - row * (course_height + spacing_y)
            
            self._draw_course_card(ax, course, x, y, course_width, course_height)
    
    def _draw_course_card(self, ax, course: Dict, x: float, y: float, width: float, height: float):
        """Draw course card with improved fonts and perfect alignment"""
        # Determine border color
        level = course.get('level', 'beginner').lower()
        border_color = self.difficulty_colors.get(level, self.colors['secondary'])
        
        # Card shadow
        shadow = FancyBboxPatch((x + 0.05, y - height - 0.05), width, height,
                               boxstyle="round,pad=0.1", 
                               facecolor='gray', alpha=0.2, zorder=1)
        ax.add_patch(shadow)
        
        # Card background with better styling
        card = FancyBboxPatch((x, y - height), width, height,
                             boxstyle="round,pad=0.1", 
                             facecolor='white', 
                             edgecolor=border_color, linewidth=2.5,
                             zorder=2)
        ax.add_patch(card)
        
        # Course content with improved fonts and spacing
        title = course.get('title', 'Course Title')
        platform = course.get('platform', 'Platform')
        rating = course.get('rating', 'N/A')
        price = course.get('price', 'Price')
        
        # Title - larger, bold font with better wrapping
        wrapped_title = textwrap.wrap(title, 35)
        title_text = wrapped_title[0] if wrapped_title else title
        ax.text(x + width/2, y - 0.3, title_text, 
                ha='center', va='center',
                fontsize=11, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['primary'], zorder=3)
        
        # Second line of title if needed
        if len(wrapped_title) > 1:
            ax.text(x + width/2, y - 0.5, wrapped_title[1], 
                    ha='center', va='center',
                    fontsize=10, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['primary'], zorder=3)
        
        # Platform - better positioned
        platform_y = y - 0.7 if len(wrapped_title) > 1 else y - 0.6
        ax.text(x + width/2, platform_y, f"🏫 {platform}", 
                ha='center', va='center',
                fontsize=9, fontfamily='sans-serif',
                color=self.colors['dark_gray'], zorder=3)
        
        # Rating and price - clearer formatting
        details_y = platform_y - 0.25
        ax.text(x + width/2, details_y, f"⭐ {rating}", 
                ha='center', va='center',
                fontsize=8, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['warning'], zorder=3)
        
        price_y = details_y - 0.2
        ax.text(x + width/2, price_y, f"💰 {price}", 
                ha='center', va='center',
                fontsize=8, fontweight='bold', fontfamily='sans-serif',
                color=self.colors['success'], zorder=3)
        
        # Level badge - better positioned and styled
        badge_width = 0.6
        badge_height = 0.25
        level_badge = FancyBboxPatch((x + width - badge_width - 0.1, y - 0.2), 
                                    badge_width, badge_height,
                                    boxstyle="round,pad=0.02",
                                    facecolor=border_color, alpha=0.9, zorder=3)
        ax.add_patch(level_badge)
        ax.text(x + width - badge_width/2 - 0.1, y - 0.075, level[:3].upper(), 
                ha='center', va='center',
                fontsize=7, fontweight='bold', fontfamily='sans-serif',
                color='white', zorder=4)
    
    def _draw_footer(self, ax, roadmap_data: Dict):
        """Draw footer with improved fonts and alignment"""
        # Footer background - better styling
        footer_rect = FancyBboxPatch((0.2, 0.2), 23.6, 4.8,
                                    boxstyle="round,pad=0.2",
                                    facecolor=self.colors['light_gray'],
                                    edgecolor=self.colors['medium_gray'],
                                    linewidth=2, alpha=0.95)
        ax.add_patch(footer_rect)
        
        # Career outcomes - left side with better fonts
        career_outcomes = roadmap_data.get('career_outcomes', [])
        if career_outcomes:
            ax.text(6, 4.5, "🚀 CAREER PATHS", 
                    ha='center', va='center',
                    fontsize=16, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['primary'])
            
            for i, outcome in enumerate(career_outcomes[:4]):
                ax.text(6, 3.9 - i*0.4, f"• {outcome}", 
                        ha='center', va='center',
                        fontsize=12, fontfamily='sans-serif',
                        color=self.colors['dark_gray'])
        
        # Salary info - right side with better styling
        salary_range = roadmap_data.get('salary_range', '')
        if salary_range:
            ax.text(18, 4.5, "💰 SALARY RANGE", 
                    ha='center', va='center',
                    fontsize=16, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['primary'])
            
            # Format salary range better
            wrapped_salary = textwrap.wrap(salary_range, 25)
            for i, line in enumerate(wrapped_salary[:2]):
                ax.text(18, 3.9 - i*0.3, line, 
                        ha='center', va='center',
                        fontsize=13, fontweight='bold', fontfamily='sans-serif',
                        color=self.colors['success'])
        
        # Industry demand - center with better formatting
        industry_demand = roadmap_data.get('industry_demand', '')
        if industry_demand:
            ax.text(12, 2.8, "📈 MARKET DEMAND", 
                    ha='center', va='center',
                    fontsize=14, fontweight='bold', fontfamily='sans-serif',
                    color=self.colors['primary'])
            wrapped_demand = textwrap.wrap(industry_demand, 50)
            for i, line in enumerate(wrapped_demand[:2]):
                ax.text(12, 2.3 - i*0.3, line, 
                        ha='center', va='center',
                        fontsize=11, fontfamily='sans-serif',
                        color=self.colors['dark_gray'])
        
        # Branding - bottom center with better font
        ax.text(12, 0.8, "Professional Learning Roadmap - AI Generated", 
                ha='center', va='center',
                fontsize=12, fontfamily='sans-serif',
                color=self.colors['medium_gray'],
                style='italic')

class ProfessionalIntegratedSystem:
    """Main integrated system"""
    
    def __init__(self):
        self.ai_client = ProfessionalAIClient(API_KEYS)
        self.visualizer = ProfessionalRoadmapVisualizer()
    
    def generate_complete_plan(self, interests: str, skills: str = "", goals: str = "") -> Dict:
        """Generate complete learning plan"""
        print("🎯 Generating Complete Professional Learning Plan")
        print("=" * 60)
        
        start_time = time.time()
        
        # Generate course recommendations
        print("📚 Step 1: Generating 8 course recommendations...")
        courses = self.ai_client.recommend_courses(interests, skills, goals)
        
        # Generate learning roadmap
        print("🗺️  Step 2: Creating 8-step learning roadmap...")
        roadmap = self.ai_client.generate_roadmap(interests)
        
        # Create visual roadmap
        print("🎨 Step 3: Creating professional visual roadmap...")
        image_path = self.visualizer.create_roadmap(roadmap, courses)
        
        end_time = time.time()
        
        return {
            'courses': courses,
            'roadmap': roadmap,
            'image_path': image_path,
            'generation_time': round(end_time - start_time, 2)
        }
    
    def display_plan(self, plan: Dict):
        """Display the complete plan"""
        courses = plan['courses']
        roadmap = plan['roadmap']
        image_path = plan['image_path']
        generation_time = plan['generation_time']
        
        print(f"\n🎓 PROFESSIONAL LEARNING PLAN COMPLETE")
        print("=" * 70)
        print(f"⏱️  Generated in {generation_time} seconds")
        print(f"🖼️  Visual roadmap: {image_path}")
        print("=" * 70)
        
        # Display roadmap overview
        print(f"\n🗺️  LEARNING ROADMAP: {roadmap.get('subject', 'Unknown')}")
        print("-" * 50)
        print(f"📖 Overview: {roadmap.get('overview', '')}")
        print(f"⏳ Total Duration: {roadmap.get('total_duration', '')}")
        print(f"📋 Prerequisites: {', '.join(roadmap.get('prerequisites', ['None']))}")
        
        # Display learning path (8 steps)
        learning_path = roadmap.get('learning_path', [])
        if learning_path:
            print(f"\n📊 8-STEP LEARNING PATH:")
            print("-" * 50)
            
            for step in learning_path:
                difficulty = step.get('difficulty', 'Unknown')
                if difficulty.lower() == 'beginner':
                    icon = "🟢"
                elif difficulty.lower() == 'intermediate':
                    icon = "🟡"
                else:
                    icon = "🔴"
                
                print(f"\n{icon} Step {step.get('step', 1)}: {step.get('title', '')}")
                print(f"   📝 {step.get('description', '')}")
                print(f"   ⏱️  Duration: {step.get('duration', '')}")
                print(f"   🎯 Milestone: {step.get('milestone', '')}")
        
        # Display courses (8 courses)
        if courses:
            print(f"\n📚 8 RECOMMENDED COURSES")
            print("=" * 70)
            
            # Categorize courses
            beginner_courses = [c for c in courses if c.get('level', '').lower() == 'beginner']
            intermediate_courses = [c for c in courses if c.get('level', '').lower() == 'intermediate'] 
            advanced_courses = [c for c in courses if c.get('level', '').lower() == 'advanced']
            
            def display_course_section(courses_list, level_name, level_icon):
                if not courses_list:
                    return
                
                print(f"\n{level_icon} {level_name} Level Courses ({len(courses_list)} courses)")
                print("-" * 50)
                
                for i, course in enumerate(courses_list, 1):
                    print(f"\n{i}. 📖 {course.get('title', 'Unknown Title')}")
                    print(f"   🏫 Platform: {course.get('platform', 'Unknown')}")
                    print(f"   👨‍🏫 Instructor: {course.get('instructor', 'Unknown')}")
                    print(f"   ⏱️  Duration: {course.get('duration', 'Unknown')}")
                    print(f"   ⭐ Rating: {course.get('rating', 'N/A')}/5")
                    print(f"   💰 Price: {course.get('price', 'Unknown')}")
                    print(f"   🎖️  Certificate: {course.get('certification', 'Unknown')}")
                    print(f"   🔗 Link: {course.get('url', 'No link available')}")
                    
                    skills = course.get('skills_gained', [])
                    if skills:
                        print(f"   🎯 Skills: {', '.join(skills)}")
            
            display_course_section(beginner_courses, "Beginner", "🟢")
            display_course_section(intermediate_courses, "Intermediate", "🟡")
            display_course_section(advanced_courses, "Advanced", "🔴")
        
        # Display career info
        career_outcomes = roadmap.get('career_outcomes', [])
        if career_outcomes:
            print(f"\n🚀 CAREER OUTCOMES:")
            for outcome in career_outcomes:
                print(f"   • {outcome}")
        
        salary_range = roadmap.get('salary_range', '')
        if salary_range:
            print(f"\n💰 SALARY RANGE: {salary_range}")
        
        print(f"\n🎨 Your professional visual roadmap: {image_path}")
        print("🚀 Ready to start your learning journey!")

def main():
    """Main function"""
    print("🎓 PROFESSIONAL AI COURSE RECOMMENDER & ROADMAP GENERATOR")
    print("=" * 70)
    print("🚀 Enhanced with professional visualization")
    print("🎨 Generate 8-step roadmaps with 8 course recommendations")
    print("=" * 70)
    
    # Check for API keys
    if not API_KEYS:
        print("\n❌ No API keys found!")
        print("   This application requires Google Gemini API keys to function.")
        print("   Please follow these steps:")
        print("   1. Go to https://makersuite.google.com/app/apikey")
        print("   2. Create an API key")
        print("   3. Create a .env file in this directory with:")
        print("      GEMINI_API_KEY_1=your_api_key_here")
        print("   4. Run the application again")
        print("\n🔧 Alternatively, you can run without AI features by modifying the code.")
        return
    
    try:
        # Get user input
        interests = input("\nWhat would you like to learn? (e.g., 'Machine Learning', 'Web Development'): ").strip()
        if not interests:
            print("❌ Please enter your learning interests.")
            return
        
        skills = input("What are your current skills? (optional): ").strip()
        goals = input("What are your career goals? (optional): ").strip()
        
        print(f"\n🎯 Creating professional learning plan for: {interests}")
        print("⏳ This may take 30-60 seconds for comprehensive results...")
        
        # Generate plan
        system = ProfessionalIntegratedSystem()
        plan = system.generate_complete_plan(interests, skills, goals)
        
        # Display results
        system.display_plan(plan)
        
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("🔧 Please check your API keys and internet connection.")

if __name__ == "__main__":
    if not API_KEYS:
        print("❌ No API keys found!")
        print("   Please set up your Gemini API keys in .env file first.")
        print("   See README.md for instructions.")
        sys.exit(1)
        
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick" and len(sys.argv) > 2:
            subject = " ".join(sys.argv[2:])
            system = ProfessionalIntegratedSystem()
            plan = system.generate_complete_plan(subject)
            system.display_plan(plan)
        elif sys.argv[1] == "--help":
            print("🎓 Professional AI Course Recommender & Roadmap Generator")
            print("Usage:")
            print("  python pro_int_courses.py                    # Interactive mode")
            print("  python pro_int_courses.py --quick 'Subject' # Quick generation")
            print("Examples:")
            print("  python pro_int_courses.py --quick 'Data Science'")
        else:
            print("❌ Unknown option. Use --help for usage information.")
    else:
        main()
