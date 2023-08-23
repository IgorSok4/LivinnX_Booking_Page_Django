// document.addEventListener("DOMContentLoaded", function() {
//     const checkboxesToday = document.querySelectorAll('.today-checkbox');
//     const checkboxesTomorrow = document.querySelectorAll('.tomorrow-checkbox');
//     const chosenHoursListToday = document.getElementById('chosen-hours-list-today');
//     const chosenHoursListTomorrow = document.getElementById('chosen-hours-list-tomorrow');
  
//     function manageHourList(checkbox, hourList) {
//         const hour = checkbox.value;
//         const isChecked = checkbox.checked;

//         if (isChecked) {
//             // Dodaj zaznaczoną godzinę do listy
//             const listItem = document.createElement('li');
//             listItem.textContent = hour;
//             hourList.appendChild(listItem);
//         } else {
//             // Usuń godzinę z listy, jeśli została odznaczona
//             const items = hourList.getElementsByTagName('li');
//             for (let i = 0; i < items.length; i++) {
//                 if (items[i].textContent === hour) {
//                     items[i].remove();
//                     break;
//                 }
//             }
//         }
//     }

//     checkboxesToday.forEach(function(checkbox) {
//         checkbox.addEventListener('change', function() {
//             manageHourList(this, chosenHoursListToday);
//         });
//     });

//     checkboxesTomorrow.forEach(function(checkbox) {
//         checkbox.addEventListener('change', function() {
//             manageHourList(this, chosenHoursListTomorrow);
//         });
//     });

// });