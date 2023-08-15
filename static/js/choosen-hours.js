document.addEventListener("DOMContentLoaded", function() {
    const checkboxes = document.querySelectorAll('.hour-checkbox');
    const chosenHoursList = document.getElementById('chosen-hours-list');
  
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const hour = this.value;
            const isChecked = this.checked;
  
            if (isChecked) {
                // Dodaj zaznaczoną godzinę do listy
                const listItem = document.createElement('li');
                listItem.textContent = hour;
                chosenHoursList.appendChild(listItem);
            } else {
                // Usuń godzinę z listy, jeśli została odznaczona
                const items = chosenHoursList.getElementsByTagName('li');
                for (let i = 0; i < items.length; i++) {
                    if (items[i].textContent === hour) {
                        items[i].remove();
                        break;
                    }
                }
            }
        });
    });
});