$(document).ready(function () {
    
    var i = 0
    
    $('#romance-right').click(function () {
        
        i++;
        
        if (i > 5){
            i=0;
        }
        
        $('#romance-grid').animate({
            left: -234.125 * i
        });
        
    });
    
    $('#romance-left').click(function () {
        
        i--;
        
        if (i < 0){
            i=5;
        }
        
        $('#romance-grid').animate({
            left: -334.125 * i
        });
        
    });
    


    $('#action-right').click(function () {
        
        i++;
        
        if (i > 5){
            i=0;
        }
        
        $('#action-grid').animate({
            left: -234.125 * i
        });
        
    });
    
    
    
    $('#action-left').click(function () {
        
        i--;
        
        if (i < 0){
            i=5;
        }
        
        $('#action-grid').animate({
            left: -334.125 * i
        });
        
    });
    
    
    

    
    $('#ani-right').click(function () {
        
        i++;
        
        if (i > 5){
            i=0;
        }
        
        $('#ani-grid').animate({
            left: -234.125 * i
        });
        
    });
    
    
    
    $('#ani-left').click(function () {
        
        i--;
        
        if (i < 0){
            i=5;
        }
        
        $('#ani-grid').animate({
            left: -334.125 * i
        });
        
    });
    
    
    



    
    $('#thriller-right').click(function () {
        
        i++;
        
        if (i > 5){
            i=0;
        }
        
        $('#thriller-grid').animate({
            left: -234.125 * i
        });
        
    });
    
    
    $('#thriller-left').click(function () {
        
        i--;
        
        if (i < 0){
            i=5;
        }
        
        $('#thriller-grid').animate({
            left: -334.125 * i
        });
        
    });
    
    
   
    
    
});/*end*/