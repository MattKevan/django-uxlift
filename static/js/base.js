document.body.addEventListener('htmx:afterSwap', function(event) {
        // Reinitialize Preline components, specifically the select element
        window.HSStaticMethods.autoInit();

});