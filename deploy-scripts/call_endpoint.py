import json
import boto3

smr_client = boto3.client("sagemaker-runtime")

if __name__ == "__main__":
    parameters = {
        "max_new_tokens": 2048,
        "temperature": 0.9,
        "top_p": 0.8,
    }

    endpoint_name = "llama3-8b-qlora-2024-11-22-01-28-32-671-endpoint"

    messages = [
        {"role": "system", "content": "입력되는 글을 바탕으로 해당 가맹점의 특정과 트랜드를 잘 표현하는 태그 3개 만들어줘. ( #태그, #태그, #태그 형식으로 나오게해줘 )"},
        {"role": "user",
         "content": "#을지로3가디저트카페#을지로3가카페#을지로디저트카페#블루커피베이크#을지로3가#힙지로카페을지로3가점심먹고더우니터벅터벅걷다가을지로3가에서후식까지알차게즐기기!위치및운영시간인쇄소골목을지로3가디저트카페50m©NAVERCorp.블루커피베이크서울특별시중구충무로4길211층✔️위치-을지로3가8번출구에서타코집골목으로쭉들어오면된다!✔️운영시간월금7시30분20시19시40분라스트오더토요일11시20시평일과라스트오더동일일요일휴무✔️☎️0507-1341-1365인쇄골목을걷다보면어?하지만간판이따로없는게힙지로스타일!요기가입구!망고빙수,팥빙수도판매중!포스터사진장난아니네🤭이래야사먹고싶나보당ㅎㅎ요즘?핫한당근라페샌드위치도판매중지원갔을때어떤분이당근라페가뭐냐고물어보셨는데대답못함....ㅜㅜ검색해보니당근샐러드라는뜻!ㅎㅎ인스타감성의작은내부모습음료메뉴판맨날같은거먹을꺼면서도고민하는나ㅋㅋ라떼와진한라떼차이는'진한라떼'우유도블랜딩해서즐길수있는라떼라고하셨다!!을지로3가디저트카페라서간단히즐길수있는디저트휘낭시에,마들렌,샌드위치도판매중!!여름이라서빙수도판매중!을지로3가디저트카페메뉴소개팥빙수,휘낭시에,ice라떼팥빙수,휘낭시에,라떼1인1메뉴이다보니디저트풍성💕1인용팥빙수와콘푸라이트메뉴판에도작게12인용이라고써져있다ㅎ목말라서시킨라떼!산미없고,부드러워서쭉쭉잘들어가긴했다ㅎㅎ문득진한라떼도궁금해졌지만이미다먹었으니패스배부르니휘낭시에는집가서엄마한테줬다ㅋ요즘휘낭시에포장해서항상엄마한테주는거같다ㅋㅋ빙수골고루비벼비벼~이때살짝오빠가나한테살짝난제질문했었다콘푸로스트가좋아?콘푸라이트가좋아?음.....둘다잘먹긴한데ㅋㅋㅋㅋ항상세일하는거만먹는타입ㅋㅋ그잠깐걸었는데도더웠는데을지로3가디저트카페에서팥빙수도먹고음료도먹고하니좋다좋아ㅋㅋ깨알같이당일날짜로표시되어있다!https://www.instagram.com/blu.koffee.bake?igsh=MW1lbW05OGdha2Vpeg==블루커피베이크(@blu.koffee.bake)•Instagram사진및동영상팔로워573명,팔로잉528명,게시물65개-블루커피베이크(@blu.koffee.bake)님의Instagram사진및동영상보기www.instagram.com을지로3가디저트카페블루커피베이크사진더많이보려면인스타구경가기!사장님께서8월오후부터샴페인과와인페이링바개시예정이라고안내해주셨다!8월에달달한샴페인한번먹으러그땐저녁에한번와봐야겠당ㅎㅎ"},
    ]

    invoke_response = smr_client.invoke_endpoint(
        EndpointName=endpoint_name,
        Body=json.dumps(
            {
                "messages": messages,
                "stream": False,
                **parameters,
            }
        ),
        ContentType="application/json",
        CustomAttributes='accept_eula=false'
    )

    # for event in invoke_response['Body']:
    #     print(event.decode('utf-8'))
    print(json.loads(invoke_response["Body"].read().decode("utf-8"))['choices'][0]['message'])
