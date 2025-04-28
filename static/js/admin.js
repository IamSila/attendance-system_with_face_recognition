
// Handle click on any "view actions" button
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('viewActions')) {
      // Find the nearest actions menu relative to the clicked button
      const actionsMenu = e.target.closest('td').querySelector('.edits');
      actionsMenu.classList.remove('hidden');
    }
    
    // Handle click on any close button
    if (e.target.classList.contains('btn-close')) {
      // Find the nearest actions menu and hide it
      const actionsMenu = e.target.closest('.edits');
      actionsMenu.classList.add('hidden');
    }
  });
