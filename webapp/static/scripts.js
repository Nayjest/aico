$(document).ready(function() {
    // Highlight diff blocks
    $('.diff-highlight').each(function() {
        $(this).addClass('language-diff'); // Add the language class for diff
        hljs.highlightElement(this);
    });

    // Highlight JSON blocks within the 'Other Details' tab
    $('.json-highlight').each(function() {
        $(this).addClass('language-json'); // Add the language class for JSON
        hljs.highlightElement(this);
    });

    // Tabs for filtering accepted, rejected and all items
    var allChangesTab = $('#allChangesTab');
    var acceptedChangesTab = $('#acceptedChangesTab');
    var rejectedChangesTab = $('#rejectedChangesTab');

    allChangesTab.click(function() {
        $('.card').show();
        allChangesTab.addClass('active');
        acceptedChangesTab.removeClass('active');
        rejectedChangesTab.removeClass('active');
    });

    acceptedChangesTab.click(function() {
        $('.card').hide().filter(function() {
            return $(this).data('decision').toLowerCase().includes('accept');
        }).show();
        acceptedChangesTab.addClass('active');
        allChangesTab.removeClass('active');
        rejectedChangesTab.removeClass('active');
    });

    rejectedChangesTab.click(function() {
        $('.card').hide().filter(function() {
            return $(this).data('decision').toLowerCase().includes('reject');
        }).show();
        rejectedChangesTab.addClass('active');
        allChangesTab.removeClass('active');
        acceptedChangesTab.removeClass('active');
    });
});