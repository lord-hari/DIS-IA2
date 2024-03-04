$(document).ready(function() {
    // Event handler for clicking on an animal image in search results
    $('#search-results').on('click', '.image-container', function() {
        // Get the animal name from the alt attribute of the clicked image
        var animalName = $(this).find('img').attr('alt');
        // Redirect to the animal details page for the clicked animal
        window.location.href = '/animal/' + animalName;
    });

    // Event handler for input changes in the search bar
    $("#searchInput").on("input", function() {
        // Get the search query from the input field
        var searchQuery = $("#searchInput").val();

        // Make an AJAX request to the /search route
        $.ajax({
            type: "GET",
            url: "/search",
            data: { search_query: searchQuery },
            dataType: 'json',
            success: function(response) {
                // Clear previous search results
                $('#search-results').empty();
                var currentRow;
                var imagesInRow = 0;

                // Iterate through each result item from the search response
                response.forEach(function(entry) {
                    // Start a new row if needed
                    if (imagesInRow === 0) {
                        currentRow = $('<div class="image-row"></div>');
                    }

                    // Create image container, image, and paragraph elements
                    var imageContainer = $('<div class="image-container"></div>');
                    var img = $('<img>').attr('src', entry.path).attr('alt', entry.name);
                    var p = $('<p class="centered"></p>').text(entry.name);

                    // Add an 'error' event listener to handle image loading errors
                    img.on('error', function() {
                        // Load default image on error
                        img.attr('src', '/static/assets/default.svg');
                        img.attr('alt', 'Default Image');
                    });

                    // Append image and paragraph to the current row
                    imageContainer.append(img, p);
                    currentRow.append(imageContainer);

                    // Increment count of images in the current row
                    imagesInRow++;

                    // If the current row is full, append it to the search results and reset variables
                    if (imagesInRow === 4) {
                        $('#search-results').append(currentRow);
                        imagesInRow = 0;
                    }
                });

                // Append the last row if it's not full
                if (imagesInRow > 0) {
                    $('#search-results').append(currentRow);
                }
            },
            error: function(error) {
                console.error("Error during search:", error);
            }
        });
    });
});

$(document).ready(function() {
    // Event handler for scrolling
    $(window).scroll(function() {
        // Check if the user has scrolled to the bottom of the page
        if ($(window).scrollTop() + $(window).height() == $(document).height()) {
            // Show the footer when at the bottom
            $('footer').slideDown();
        } else {
            // Hide the footer when not at the bottom
            $('footer').slideUp();
        }
    });
});