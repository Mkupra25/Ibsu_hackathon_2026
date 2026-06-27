"""
Chat endpoint — მთავარი საუბრის API.

📌 პრეზენტაციისთვის:
ეს არის მთავარი endpoint, რომელსაც React ფრონტენდი იძახებს.
მომხმარებლის ქართული კითხვა შემოდის, და სრული პასუხი ბრუნდება:
- ტექსტური პასუხი ქართულად
- გენერირებული SQL
- მოთხოვნის შედეგი (ცხრილი)
- გრაფიკის შეთავაზება
"""

from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse, ExampleQuestion
from app.services.pipeline import pipeline

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="ბიზნეს-ანალიტიკის შეკითხვა",
    description="გაგზავნეთ ქართული ბიზნეს-კითხვა და მიიღეთ AI-ის პასუხი SQL მონაცემთა ბაზიდან",
)
async def chat(request: ChatRequest):
    """
    მთავარი საუბრის endpoint.
    
    მომხმარებლის შეტყობინებას pipeline-ში გატარებს:
    ინტენტი → სქემა → SQL → ვალიდაცია → შესრულება → ფორმატირება
    """
    response = await pipeline.process_message(
        message=request.message,
        conversation_id=request.conversation_id,
    )
    return response


@router.get(
    "/examples",
    response_model=list[ExampleQuestion],
    summary="სადემონსტრაციო კითხვები",
    description="ქართული ბიზნეს-კითხვების მაგალითები, რომლებიც შეგიძლიათ სცადოთ",
)
async def get_examples():
    """სადემონსტრაციო კითხვების სია ფრონტენდისთვის."""
    return [
        ExampleQuestion(
            question="რა არის ჩვენი ჯამური შემოსავალი?",
            category="შემოსავალი",
            description="ყველა შეკვეთის ჯამური თანხა",
        ),
        ExampleQuestion(
            question="აჩვენე გაყიდვები ქალაქების მიხედვით",
            category="გეოგრაფია",
            description="შემოსავალი და შეკვეთები ქალაქების მიხედვით",
        ),
        ExampleQuestion(
            question="ტოპ 5 პროდუქტი გაყიდვებით",
            category="პროდუქტები",
            description="ყველაზე გაყიდვადი პროდუქტები",
        ),
        ExampleQuestion(
            question="რომელ პროდუქტებს აქვთ ყველაზე მაღალი მოგების ზღვარი?",
            category="მოგება",
            description="პროდუქტები მოგების პროცენტის მიხედვით",
        ),
        ExampleQuestion(
            question="შეადარე ამ თვის შეკვეთები გასულ თვეს",
            category="ტრენდები",
            description="თვეების შედარება",
        ),
        ExampleQuestion(
            question="რამდენი ახალი მომხმარებელი დარეგისტრირდა ბოლო 3 თვეში?",
            category="მომხმარებლები",
            description="ახალი რეგისტრაციები",
        ),
        ExampleQuestion(
            question="რა არის საშუალო შეკვეთის თანხა გადახდის მეთოდის მიხედვით?",
            category="გადახდები",
            description="ბარათი vs ნაღდი vs განვადება",
        ),
        ExampleQuestion(
            question="აჩვენე კატეგორიების მიხედვით გაყიდვების დინამიკა თვეების მიხედვით",
            category="ტრენდები",
            description="კატეგორიების თვიური დინამიკა",
        ),
        ExampleQuestion(
            question="ვინ არიან ჩვენი ტოპ 10 მომხმარებელი ხარჯვის მიხედვით?",
            category="მომხმარებლები",
            description="ყველაზე აქტიური მომხმარებლები",
        ),
        ExampleQuestion(
            question="რომელ რეგიონში გვაქვს ყველაზე მეტი გაუქმებული შეკვეთა?",
            category="ანალიზი",
            description="გაუქმების ანალიზი რეგიონების მიხედვით",
        ),
    ]
