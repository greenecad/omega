const endDate = '20 April 2026, 7:00 AM';
    //Printing end time
    document.querySelector('.cd-end-time'). innerText = endDate;
    //selects all inputs 
    let input = document.querySelectorAll('input');
    const countDown = () => {
        //Will add countdown date inside new date
        let newDate = new Date(endDate); 
        //Get dynamic date
        let now = new Date();
        //It will minus our end date with present time and gives value in seconds
        let diff = (newDate - now) / 1000; 
        //return default value 00 when date ends
        if(diff < 0) {
            document.getElementById('.cd-end-time').style.display = 'none';
        }
        //Lets convert these seconds into remaining days, hours, minutes, and seconds
        input[0].value = Math.floor(diff / 3600 / 24) //This will give us remaining days
        input[1].value = Math.floor((diff / 3600) % 24) //This will give us remaining hours
        input[2].value = Math.floor((diff / 60) % 60) //This will give us remaining minutes
        input[3].value = Math.floor((diff) % 60) //This will give us remaining seconds
    }
    //Initial Call
    countDown();
    //lets make seconds working
    setInterval(() => {
        //Call function every second = 1000ms
        countDown();
    }, 1000);