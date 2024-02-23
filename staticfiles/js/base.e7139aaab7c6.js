document.body.addEventListener('htmx:afterSwap', function(event) {
        // Reinitialize Preline components, specifically the select element
        window.HSStaticMethods.autoInit();
       

});
document.body.addEventListener('htmx:afterSwap', function(event) {
  if (event.detail.target.contains(document.querySelector('[x-data]'))) {
    Alpine.discoverUninitializedComponents((el) => {
      Alpine.initializeComponent(el);
    });
  }
});

document.body.addEventListener('postSaved', function(event) {
    // Assuming the success message is sent via Django messages and rendered in a hidden div
    const messageDiv = document.getElementById('success-message');
    if (messageDiv) {
        messageDiv.classList.remove('hidden'); // Make the success message visible
        messageDiv.innerText = event.detail.message; // Update the message text if needed
    }
});