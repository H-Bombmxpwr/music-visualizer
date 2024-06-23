$(document).ready(function () {
    function fetchWikipediaInfo(song, album, artist) {
        $.ajax({
            type: 'POST',
            url: '/get_wikipedia_info',
            contentType: 'application/json',
            data: JSON.stringify({ query: `${song} ${artist}`, type: 'song' }),
            success: function (data) {
                if (data.error) {
                    $('#song-info').html(`<p>${data.error}</p>`);
                } else {
                    $('#song-info').html(`<p>${data.content}</p><div>${data.images.map((image, idx) => `<img src="${image}" alt="Image"><caption>${data.captions[idx]}</caption>`).join('')}</div>`);
                }
            },
            error: function () {
                $('#song-info').text('No information found.');
            }
        });

        $.ajax({
            type: 'POST',
            url: '/get_wikipedia_info',
            contentType: 'application/json',
            data: JSON.stringify({ query: `${album} ${artist}`, type: 'album' }),
            success: function (data) {
                if (data.error) {
                    $('#album-info').html(`<p>${data.error}</p>`);
                } else {
                    $('#album-info').html(`<p>${data.content}</p><div>${data.images.map((image, idx) => `<img src="${image}" alt="Image"><caption>${data.captions[idx]}</caption>`).join('')}</div>`);
                }
            },
            error: function () {
                $('#album-info').text('No information found.');
            }
        });

        $.ajax({
            type: 'POST',
            url: '/get_wikipedia_info',
            contentType: 'application/json',
            data: JSON.stringify({ query: artist, type: 'artist' }),
            success: function (data) {
                if (data.error) {
                    $('#artist-info').html(`<p>${data.error}</p>`);
                } else {
                    $('#artist-info').html(`<p>${data.content}</p><div>${data.images.map((image, idx) => `<img src="${image}" alt="Image"><caption>${data.captions[idx]}</caption>`).join('')}</div>`);
                }
            },
            error: function () {
                $('#artist-info').text('No information found.');
            }
        });

        $('#sidebar').show();
    }

    $('.tab').click(function () {
        $('.tab').removeClass('active');
        $(this).addClass('active');

        $('.content').removeClass('active');
        $('#' + $(this).data('content')).addClass('active');
    });

    window.fetchWikipediaInfo = fetchWikipediaInfo;

    function closeSidebar() {
        $('#sidebar').hide();
    }

    window.closeSidebar = closeSidebar;
});
