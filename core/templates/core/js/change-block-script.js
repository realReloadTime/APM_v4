document.addEventListener('DOMContentLoaded', function() {
    let select = document.getElementById('enviroment-type');
    let block = document.querySelectorAll('.changing-form');
    let lastIndex = 0; 

    select.addEventListener('change', function() {
        block[lastIndex].style.display = "none"; 

        let index = select.selectedIndex; 
        block[index].style.display = "block"; 

        lastIndex = index; 
    });
});