function setUp() {
    var form = document.getElementById("aForm");
    var review = document.createElement("textarea");
    review.name = "review";
    review.cols = "80";
    review.rows = "10";
    review.placeholder = "Please enter your review here"

    var rating = document.createElement("select");
    rating.name = "rating";
    var option = document.createElement("option");
    option.value = 1;
    option.text = "Rating";
    rating.appendChild(option);
    for (var i = 1; i <= 5; i++) {
        var option = document.createElement("option");
        option.value = i;
        option.text = i;
        rating.appendChild(option);
    }
    rating.selectedIndex = 0;

    var input = document.createElement("input");
    input.setAttribute("type", "submit");
    input.name = "submit";
    input.value = "Submit";

    comment.appendChild(review);
    grade.appendChild(rating);
    subButton.appendChild(input);
}
