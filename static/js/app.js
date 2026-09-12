const budgetModal =
    document.getElementById("budget-modal");

const openBudgetButton =
    document.getElementById("open-budget");

const closeBudgetButton =
    document.getElementById("close-budget");


function openBudgetModal() {
    budgetModal.classList.add("active");
}


function closeBudgetModal() {
    budgetModal.classList.remove("active");
}


openBudgetButton.addEventListener(
    "click",
    openBudgetModal
);


closeBudgetButton.addEventListener(
    "click",
    closeBudgetModal
);


budgetModal.addEventListener("click", (event) => {
    if (event.target === budgetModal) {
        closeBudgetModal();
    }
});


const progressBar =
    document.getElementById("budget-progress-value");


if (progressBar) {
    const progress =
        Number(progressBar.dataset.progress);

    if (Number.isFinite(progress)) {
        const safeProgress =
            Math.min(
                Math.max(progress, 0),
                100
            );

        progressBar.style.width =
            `${safeProgress}%`;
    }
}


/* Editar produto */

const editModal =
    document.getElementById("edit-modal");

const closeEditButton =
    document.getElementById("close-edit");

const editForm =
    document.getElementById("edit-form");

const editProductInput =
    document.getElementById("edit-product");

const editCategoryInput =
    document.getElementById("edit-category");

const editPriceInput =
    document.getElementById("edit-price");

const editQuantityInput =
    document.getElementById("edit-quantity");


function openEditModal(button) {
    const id = button.dataset.id;

    editProductInput.value =
        button.dataset.name;

    editCategoryInput.value =
        button.dataset.category;

    editPriceInput.value =
        button.dataset.price;

    editQuantityInput.value =
        button.dataset.quantity;

    editForm.action =
        `/produto/${id}/editar`;

    editModal.classList.add("active");
}


function closeEditModal() {
    editModal.classList.remove("active");
}


document
    .querySelectorAll(".edit-product")
    .forEach((button) => {

        button.addEventListener(
            "click",
            () => openEditModal(button)
        );

    });


closeEditButton.addEventListener(
    "click",
    closeEditModal
);


editModal.addEventListener("click", (event) => {
    if (event.target === editModal) {
        closeEditModal();
    }
});


/* Busca e filtros */

const searchInput =
    document.getElementById("product-search");

const filterButtons =
    document.querySelectorAll(".filter-button");

const shoppingItems =
    document.querySelectorAll(".shopping-item");

const filterEmpty =
    document.getElementById("filter-empty");

let currentFilter = "all";


function normalizeText(text) {
    return text
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}


function filterProducts() {
    if (!searchInput) {
        return;
    }

    const searchTerm =
        normalizeText(searchInput.value);

    let visibleItems = 0;


    shoppingItems.forEach((item) => {
        const name =
            normalizeText(item.dataset.name);

        const category =
            normalizeText(item.dataset.category);

        const status =
            item.dataset.status;


        const matchesSearch =
            name.includes(searchTerm)
            || category.includes(searchTerm);


        const matchesFilter =
            currentFilter === "all"
            || status === currentFilter;


        const shouldShow =
            matchesSearch
            && matchesFilter;


        item.classList.toggle(
            "filtered-out",
            !shouldShow
        );


        if (shouldShow) {
            visibleItems += 1;
        }
    });


    if (filterEmpty) {
        filterEmpty.style.display =
            visibleItems === 0
                ? "block"
                : "none";
    }
}


if (searchInput) {
    searchInput.addEventListener(
        "input",
        filterProducts
    );
}


filterButtons.forEach((button) => {
    button.addEventListener("click", () => {

        currentFilter =
            button.dataset.filter;

        filterButtons.forEach(
            (filterButton) => {
                filterButton.classList.remove(
                    "active"
                );
            }
        );

        button.classList.add("active");

        filterProducts();
    });
});


/* Tecla Escape */

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeBudgetModal();
        closeEditModal();
    }
});

/* Barras das categorias */

const categoryBars =
    document.querySelectorAll(
        ".category-bar-value"
    );


categoryBars.forEach((bar) => {
    const progress =
        Number(
            bar.dataset.categoryProgress
        );

    if (Number.isFinite(progress)) {
        const safeProgress =
            Math.min(
                Math.max(progress, 0),
                100
            );

        bar.style.width =
            `${safeProgress}%`;
    }
});