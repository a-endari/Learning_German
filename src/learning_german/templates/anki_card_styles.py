"""CSS styles for Anki cards."""

CARD_STYLES = """
/* Light mode styles (default) */
.card {
    font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    text-align: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf0 100%);
    padding: 25px;
    max-width: 600px;
    margin: 0 auto;
    border-radius: 15px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.front-side {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}

.front-side .word {
    font-size: 26px;
    font-weight: bold;
    color: #1e88e5;
    margin-bottom: 10px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.back-side {
    text-align: left;
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    color: #333333;
}

.translations {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f0f8ff;
    border-radius: 8px;
    border-left: 5px solid #42a5f5;
    color: #333333;
}

.example {
    background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
    border-left: 5px solid #29b6f6;
    padding: 15px;
    margin-top: 20px;
    border-radius: 10px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.05);
}

.example h3 {
    margin-top: 0;
    color: #0277bd;
    font-size: 20px;
    font-weight: 600;
}

.example-content {
    font-size: 16px;
    line-height: 1.5;
    color: #01579b;
}

hr {
    height: 2px;
    background: linear-gradient(to right, #42a5f5, #29b6f6, #0288d1);
    border: none;
    margin: 20px 0;
    border-radius: 2px;
}

/* Dark mode styles */
html.night-mode, body.night-mode, #qa.night-mode, .night-mode * {
    background-color: #121826 !important;
    color: #ffffff !important;
}

.night-mode .card {
    font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    text-align: center;
    background: #1a202c !important;
    padding: 25px;
    max-width: 600px;
    margin: 0 auto;
    border-radius: 15px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
    border: 1px solid #2d3748 !important;
}

.night-mode .front-side {
    background-color: #2d3748 !important;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    margin-bottom: 15px;
}

.night-mode .front-side .word {
    color: #63b3ed !important;
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 10px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    background-color: transparent !important;
}

.night-mode .back-side {
    text-align: left;
    background-color: #2d3748 !important;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    color: #ffffff !important;
}

.night-mode .translations {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 20px;
    padding: 15px;
    background-color: #3a506b !important;
    border-radius: 8px;
    border-left: 5px solid #4299e1 !important;
    color: #ffffff !important;
}

.night-mode .translations * {
    color: #ffffff !important;
    background-color: transparent !important;
}

.night-mode .example {
    background: #3a506b !important; /* Solid color instead of gradient */
    border-left: 5px solid #4299e1 !important;
    padding: 15px;
    margin-top: 20px;
    border-radius: 10px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.2);
}

.night-mode .example h3 {
    margin-top: 0;
    color: #90cdf4 !important;
    font-size: 20px;
    font-weight: 600;
    background-color: transparent !important;
}

.night-mode .example-content {
    font-size: 16px;
    line-height: 1.5;
    color: #ffffff !important;
    background-color: transparent !important;
}

.night-mode hr {
    height: 2px;
    background-color: #4299e1 !important;
    border: none;
    margin: 20px 0;
    border-radius: 2px;
}

.night-mode #answer {
    background-color: transparent !important;
}

.night-mode #answer * {
    background-color: transparent !important;
}

.night-mode .card-content {
    background-color: transparent !important;
    color: #ffffff !important;
}

.night-mode .card-content * {
    color: #ffffff !important;
    background-color: #3a506b !important;
}
"""

# JavaScript for applying dark mode automatically based on system preference
CARD_FRONT_EXTRA = """
<script>
// Apply dark mode based on system preference
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.body.classList.add('night-mode');
    document.documentElement.classList.add('night-mode');
    
    // Force dark background on all elements
    document.querySelectorAll('*').forEach(function(el) {
        el.classList.add('night-mode');
        
        // Card container
        if (el.classList.contains('card')) {
            el.style.backgroundColor = '#1a202c';
        }
        
        // Card sides
        if (el.classList.contains('front-side') || el.classList.contains('back-side')) {
            el.style.backgroundColor = '#2d3748';
        }
        
        // Translations and examples with lighter background
        if (el.classList.contains('translations') || el.classList.contains('example')) {
            el.style.backgroundColor = '#3a506b';
        }
        
        // Text elements should have transparent background
        if (el.tagName === 'SPAN' || el.tagName === 'P' || el.tagName === 'H1' || 
            el.tagName === 'H2' || el.tagName === 'H3' || el.tagName === 'H4' || 
            el.tagName === 'DIV' && (el.classList.contains('word') || el.classList.contains('example-content'))) {
            el.style.backgroundColor = 'transparent';
        }
        
        // Horizontal rule
        if (el.tagName === 'HR') {
            el.style.backgroundColor = '#4299e1';
        }
        
        // Card content
        if (el.classList.contains('card-content')) {
            el.style.backgroundColor = 'transparent';
        }
    });
    
    // Specifically target the answer element and its children
    var answerEl = document.getElementById('answer');
    if (answerEl) {
        answerEl.style.backgroundColor = 'transparent';
        Array.from(answerEl.children).forEach(function(child) {
            child.style.backgroundColor = 'transparent';
        });
    }
}
</script>
"""