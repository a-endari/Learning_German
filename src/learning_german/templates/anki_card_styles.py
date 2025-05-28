"""CSS styles for Anki cards."""

CARD_STYLES = """
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
