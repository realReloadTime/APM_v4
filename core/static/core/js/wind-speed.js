document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('input-wind-speed');
    const output = document.getElementById('output-wind-group');

    input.addEventListener('change', function(event) {
        const speed = event.target.value;
        ChangeOutput(speed);
    });
    
    function ChangeOutput(speed){
        if (speed < 0.2){
            output.value = "Штиль";
        }
        else if (speed < 1.5){
            output.value = "Тихий";
        }
        else if (speed < 3.3){
            output.value = "Легкий";
        }
        else if (speed < 5.4){
            output.value = "Слабый";
        }
        else if (speed < 7.9){
            output.value = "Умеренный";
        }
        else if (speed < 10.7){
            output.value = "Свежий";
        }
        else if (speed < 13.8){
            output.value = "Сильный";
        }
        else if (speed < 17.1){
            output.value = "Крепкий";
        }
        else if (speed < 20.7){
            output.value = "Очень крепкий";
        }
        else if (speed < 24.4){
            output.value = "Шторм";
        }
        else if (speed < 28.4){
            output.value = "Сильный шторм";
        }
        else if (speed < 32.6){
            output.value = "Жесткий шторм";
        }
        else {
            output.value = "Ураган";
        }
    }
})