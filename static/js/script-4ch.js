'use strict';

function scroll_down() {
    setTimeout(function () {
        window.scrollTo(0, document.body.scrollHeight);
    }, 300);
}
scroll_down()

// window.addEventListener('load', function() {
//     let scrollPosition = localStorage.getItem('scrollPosition');
//     if (scrollPosition !== null) {
//     window.scrollTo(0, parseInt(scrollPosition));
//     }
// });
// window.addEventListener('scroll', function() {
//     localStorage.setItem('scrollPosition', window.scrollY);
// });


let videoActive = false
let actualvideo_play
let video
let video_play
let initialXSave
let initialYSave
let currentXSave
let currentYSave
let vidio_init = true
let scale = window.innerWidth / 2; // Начальный масштаб
let speed = 70
let video_play_arr = document.querySelectorAll('.video_play_block')
let video_play_value_save
let video_width_default = true


let video_play_content
function videoOn(post_id) { // video click
    if (video_play != undefined) {
        video_play.style.display = 'none'
        video.pause();
    }

    actualvideo_play = `video_play_${post_id}`
    video_play = document.getElementById(`video_play_${post_id}`)
    video = document.getElementById(`video_${post_id}`)


    video_play.style.width = `${scale}px`;
    video.style.width = `${scale}px`;

    // let video_play_width = ++video_play.style.width
    // let video_play_height = ++video_play.style.height

    video_play.style.zIndex = '3'

    if (video_play != undefined) {
        video_play.style.left = currentX + 'px';
        video_play.style.top = currentY + 'px';
    }


    // addEventListener addEventListener addEventListener
    video_play.addEventListener('mousedown', (e) => {
        isDragging = true;
        initialX = e.clientX - video_play.getBoundingClientRect().left;
        initialY = e.clientY - video_play.getBoundingClientRect().top;
        video_play.classList.add('dragging');
    });
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        e.preventDefault();

        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;

        video_play.style.left = currentX + 'px';
        video_play.style.top = currentY + 'px';
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        video_play.classList.remove('dragging');
    });
    // addEventListener addEventListener addEventListener

    video_play.style.display = 'block'

    let screenWidth = window.innerWidth;
    let rect = video_play.getBoundingClientRect();
    console.log(rect.top, rect.left)
    if (vidio_init
        || video_play.offsetTop < 0
        || video_play.offsetLeft < 0
        || video_play.offsetLeft > screenWidth - 10
        || video_play.offsetTop > screenWidth - 10
    ) {
        initialX = video_play.getBoundingClientRect().left;
        initialY = video_play.getBoundingClientRect().top;
        console.log(parseFloat(video_play.style.height))
        video_play.style.width = `${window.innerWidth / 2}px`
        video.style.width = `${window.innerWidth / 2 }px`
        scale = window.innerWidth / 2
        currentX = window.innerWidth / 2 - parseFloat(video_play.style.width) / 2;
        currentY = window.innerHeight / 8;
        video_play.style.left = currentX + 'px';
        video_play.style.top = currentY + 'px';
        vidio_init = false
    }

    videoActive = true
    video.currentTime = 0;
    video.play();
}

// function setBlockPosition(block, x, y) {
//     block.style.left = x + 'px';
//     block.style.top = y + 'px';
// }


let closestPopup
let closestButton
document.addEventListener('click', function (event) {
    if (videoActive === true) {
        closestPopup = event.target.closest(`#${actualvideo_play}`);
        closestButton = event.target.closest('#vid');
        if (closestPopup === null && closestButton === null) {
            video.pause();
            video_play.style.display = 'none';
            videoActive = false;
        }
    }
})


let isDragging = false;
let initialX, initialY, currentX, currentY;

let scaleSave = scale
video_play_arr.forEach((video_play) => {
    video_play.addEventListener('wheel', (e) => {
        e.preventDefault(); // Отменить стандартное поведение скроллинга
        scaleSave = scale
        let delta = Math.max(-1, Math.min(1, e.deltaY));
        // Изменить масштаб в зависимости от направления скроллинга
        if (delta < 0) {
            scale += speed;
        } else {
            if (scale > 200) {
                scale -= speed;

            }
        }
        // Применить масштабирование к элементу
        video_play.style.width = `${scale}px`;
        video.style.width = `${scale}px`;
        let deltall = scaleSave - scale
        currentX = currentX + deltall / 2
        currentY = currentY + deltall / 4
        video_play.style.left = `${currentX}px`;
        video_play.style.top = `${currentY}px`;
    });
})

let video_arr = document.querySelectorAll('.video_arr');

video_arr.forEach((video) => {
    video.addEventListener('mouseup', function () {
        setTimeout(function () {
            video.play();
        }, 1);
    });
});

let newVideoInit_i = 0
function newVideoInit() {
    let video_arr = document.querySelectorAll('.video_arr_new');
    video_arr[newVideoInit_i].addEventListener('mouseup', function () {
        setTimeout(function () {
            video.play();
        }, 1);
    });
    let video_play_arr = document.querySelectorAll('.video_play_block_new')
    video_play_arr[newVideoInit_i].addEventListener('wheel', (e) => {
        e.preventDefault(); // Отменить стандартное поведение скроллинга
        scaleSave = scale
        let delta = Math.max(-1, Math.min(1, e.deltaY));
        // Изменить масштаб в зависимости от направления скроллинга
        if (delta < 0) {
            scale += speed;
        } else {
            if (scale > 200) {
                scale -= speed;

            }
        }
        // Применить масштабирование к элементу
        video_play.style.width = `${scale}px`;
        video.style.width = `${scale}px`;
        let deltall = scaleSave - scale
        currentX = currentX + deltall / 2
        currentY = currentY + deltall / 4
        video_play.style.left = `${currentX}px`;
        video_play.style.top = `${currentY}px`;
    });
    ++newVideoInit_i
}
