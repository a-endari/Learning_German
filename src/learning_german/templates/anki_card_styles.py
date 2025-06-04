"""CSS styles for Anki cards."""

CARD_STYLES = """
/* Dark mode toggle - add a class to the card */
.card.night-mode {
    color: #e0e0e0;
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
}

.night-mode .front-side {
    background-color: #2d3748;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.night-mode .front-side .word {
    color: #63b3ed;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.night-mode .back-side {
    background-color: #2d3748;
    color: #e0e0e0;
}

.night-mode .translations {
    background-color: #2a4365;
    border-left: 5px solid #4299e1;
    color: #e0e0e0;
}

.night-mode .example {
    background: linear-gradient(135deg, #2c5282 0%, #2b6cb0 100%);
    border-left: 5px solid #4299e1;
}

.night-mode .example h3 {
    color: #90cdf4;
}

.night-mode .example-content {
    color: #e0e0e0;
}

.night-mode hr {
    background: linear-gradient(to right, #4299e1, #63b3ed, #90cdf4);
}

/* Toggle button */
#dark-mode-toggle {
    position: fixed;
    top: 10px;
    right: 10px;
    padding: 5px 10px;
    background: #ddd;
    border-radius: 5px;
    cursor: pointer;
    z-index: 100;
}

.night-mode #dark-mode-toggle {
    background: #555;
    color: #fff;
}

/* Regular styles */
.card {
    font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    text-align: center;
    color: #333;
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
"""

# JavaScript for toggling dark mode
CARD_FRONT_EXTRA = """
<div id="dark-mode-toggle" onclick="toggleDarkMode()">🌓</div>
<script>
function toggleDarkMode() {
    document.querySelector('.card').classList.toggle('night-mode');
    localStorage.setItem('darkMode', document.querySelector('.card').classList.contains('night-mode'));
}

// Check saved preference
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.querySelector('.card').classList.add('night-mode');
    }
});
</script>
"""