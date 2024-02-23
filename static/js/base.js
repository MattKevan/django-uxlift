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
function reinitializeTinyMCE(selector) {
  // Remove any existing instances from the target area to avoid duplicates
  tinymce.remove(selector);

  // Initialize TinyMCE on new content
  tinymce.init({
    selector: selector,
    // Add any TinyMCE configuration options you need
  });
}

document.body.addEventListener('htmx:afterSwap', function(event) {
  // Check if the swapped content contains elements that need TinyMCE
  if (event.detail.target.querySelector('.tinymce')) {
    reinitializeTinyMCE('.tinymce');
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