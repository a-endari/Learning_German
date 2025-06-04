"""CSS styles for Anki cards."""

CARD_STYLES = """
/* Override everything with !important */
html, body, #qa, .card, * {
    background-color: #121826 !important;
    color: #ffffff !important;
}

/* Card specific styles */
.card {
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

.front-side {
    background-color: #2d3748 !important;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    margin-bottom: 15px;
}

.front-side .word {
    color: #63b3ed !important;
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 10px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.back-side {
    text-align: left;
    background-color: #2d3748 !important;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    color: #ffffff !important;
}

.translations {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 20px;
    padding: 15px;
    background-color: #2a4365 !important;
    border-radius: 8px;
    border-left: 5px solid #4299e1 !important;
    color: #ffffff !important;
}

.translations * {
    color: #ffffff !important;
}

.example {
    background: linear-gradient(135deg, #2c5282 0%, #2b6cb0 100%) !important;
    border-left: 5px solid #4299e1 !important;
    padding: 15px;
    margin-top: 20px;
    border-radius: 10px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.2);
}

.example h3 {
    margin-top: 0;
    color: #90cdf4 !important;
    font-size: 20px;
    font-weight: 600;
}

.example-content {
    font-size: 16px;
    line-height: 1.5;
    color: #ffffff !important;
}

hr {
    height: 2px;
    background: linear-gradient(to right, #4299e1, #63b3ed, #90cdf4) !important;
    border: none;
    margin: 20px 0;
    border-radius: 2px;
}

.card-content {
    background-color: #2d3748 !important;
    color: #ffffff !important;
}

.card-content * {
    color: #ffffff !important;
}
"""

# JavaScript for applying dark mode automatically based on system preference
CARD_FRONT_EXTRA = """
<script>
// Force dark background on all elements
document.querySelectorAll('*').forEach(function(el) {
    el.style.backgroundColor = '#121826';
    if (el.classList.contains('card')) {
        el.style.backgroundColor = '#1a202c';
    }
    if (el.classList.contains('front-side') || el.classList.contains('back-side')) {
        el.style.backgroundColor = '#2d3748';
    }
    if (el.tagName === 'HR') {
        el.style.background = 'linear-gradient(to right, #4299e1, #63b3ed, #90cdf4)';
    }
});
</script>
"""