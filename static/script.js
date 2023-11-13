// Získání checkboxu
const categoryCheckboxes = document.querySelectorAll('input[type="checkbox"].category-checkbox');
const storeCheckboxes = document.querySelectorAll('input[type="checkbox"].store-checkbox')

// Filtrování produktů
categoryCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', filterProducts);
});
storeCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        filterProducts();
        updateCategoryButtonVisibility();
    });
});
 
// Funkce pro filtrování produktů
function filterProducts() {
    // Získá vybrané kategorie
    const selectedCategories = Array.from(categoryCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
    const selectedStore = Array.from(storeCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
    // Získá všechny produkty
    const products = document.querySelectorAll('.product-row');

    // Projde produkty a zobrazí nebo skryjte podle vybraných kategorií
    products.forEach(product => {
        const productCategories = Array.from(product.querySelectorAll('.product-category'))
            .map(categoryElement => categoryElement.textContent);
        const productStore = product.querySelector('.product-store').textContent;
        const categoryMatch = selectedCategories.length === 0 || selectedCategories.some(category => productCategories.includes(category));
        const storeMatch = selectedStore.length === 0 || selectedStore.includes(productStore);
        if (categoryMatch && storeMatch) {
            product.style.display = 'table-row'; // Zobrazit produkt
        } else {
            product.style.display = 'none'; // Skrýt produkt
        }
    });
    updateButtonStyles();
}

// Stisknutí tlačítka
function updateButtonStyles() {
    categoryCheckboxes.forEach(checkbox => {
        const customButton = checkbox.nextElementSibling; // Získá následující element (tlačítko)
        if (checkbox.checked) {
            customButton.style.backgroundColor = '#e74c3c'; // Změní barvu tlačítka
        } else {
            customButton.style.backgroundColor = '#3498db'; // Vrátí původní barvu tlačítka
        }
    });
}

// Zobrazení tlačítek kategorií
function updateCategoryButtonVisibility() {
    const anyStoreChecked = Array.from(storeCheckboxes).some(checkbox => checkbox.checked);
    categoryCheckboxes.forEach(checkbox => {
        const customButton = checkbox.nextElementSibling;
        customButton.style.display = anyStoreChecked ? 'block' : 'none';
    });
}

// Skryjte tlačítka s kategoriemi ve výchozím stavu
updateCategoryButtonVisibility();