document.addEventListener('DOMContentLoaded', function(){

    hide_lesson_forms();

    document.querySelectorAll('.postpone-lesson-link').forEach(link => {
        link.onclick = function() {
            if (document.querySelector(`#postpone-${link.dataset.lesson}`).style.display == 'none'){
                hide_lesson_forms();
                document.querySelector(`#postpone-${link.dataset.lesson}`).style.display = 'inline';
            }
            else{
                hide_lesson_forms();
            }
        }
    })
})

function hide_lesson_forms(){
    document.querySelectorAll('.postpone-lesson-form').forEach(form =>{
        form.style.display = 'none';
    })
}