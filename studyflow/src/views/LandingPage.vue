<template>
  <div class="landing-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <h1 style="font-size: 7em;">StudyFlow</h1>
      <h2>ỨNG DỤNG QUẢN LÝ HỌC TẬP CÁ NHÂN</h2>
      <br> 
      <br>
      <br>
      <h2 style="font-size: 1.3em; color: white;" class="motivational-quote">"{{ randomQuote }}"</h2>
      <br>
      <br>
      <div class="button-group">
        <button class="btn login-btn" @click="goToLogin">Đăng nhập</button>
        <button class="btn register-btn" @click="goToRegister">Đăng ký</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { useRouter } from 'vue-router';
import {ref, onMounted} from 'vue';

const router = useRouter();

const goToLogin = () => {
  router.push("/login")
}

const goToRegister = () => {
  router.push("/register");
}

const quotes = [
  "Lúc này nếu ngủ bạn sẽ có một giấc mơ, nhưng lúc này nếu học bạn sẽ giải thích được giấc mơ!",
  "Ngày hôm nay nếu bạn lãng phí đồng nghĩa với việc bạn bóp chết quá khứ và vứt bỏ ngày mai. Ngày hôm nay qua đi nó sẽ không bao giờ trở lại.",
  "Sự khổ nhọc khi học chỉ là tạm thời, sự đau khổ vì không học đến nơi là mãi mãi.",
  "Khi bạn cảm thấy quá muộn, sự thật là vẫn còn sớm. Đó chính là thời điểm bắt đầu hành động.", 
  "Hạnh phúc không có thứ tự, nhưng thành công thì có!", 
  "Học tập phải chăng là nhiệm vụ cả đời, ngay cả người học cũng không thể chứng minh còn có thể làm gì.",
  "Hãy đón nhận sự khó nhọc không thể chối từ.",
  "Người đầu tư cho tương lai là người thực hiện đến cùng.",
  "Nỗ lực để trở thành phiên bản mà bạn thích nhất. Cho dù không thành công, ít nhất bạn cảm thấy thích dáng vẻ nỗ lực của bản thân ở hiện tại!",
  "Dừng những việc làm bạn hao tổn tinh thần, dừng những việc không có ý nghĩa. Cậu nên dành thời gian đó để đọc sách, để vận động, để yêu thương, để cố gắng chạm tới cuộc sống mà bạn mong muốn.",
  "Đừng cảm thấy 'một mình' là kỳ quái. Những ngày bình thường luôn yên lặng, an tĩnh như thế. Cũng đừng sợ rằng nỗ lực không có kết quả, sự lo lắng chỉ làm bạn thêm gánh nặng mà thôi.",
  "Còn chưa tới cuối cùng sao bạn biết rằng mình không thể?",
  "Vứt bỏ thái độ không tốt, vứt bỏ thói quen trì hoãn. Đã xác định đi con đường nào thì đừng chỉ lo để ý nó còn bao xa, chỉ cần tiến bước về phía trước, mỗi dấu chân của bạn đều sẽ trở thành kinh nghiệm và sức mạnh cho bạn sau này!",
  "Yên lặng mà làm, đợi thành công rồi nói tiếp!", 
  "Trạng thái tốt nhất của một người chính là biết bản thân mình muốn gì và dốc hết sức vì nó.",
  "Có những việc, không phải cứ nhìn thấy hy vọng thì mới kiên trì, mà là phải kiên trì thì mới có thể nhìn thấy.",
  "Con người không nên sợ áp lực trong cuộc sống, bởi vì có áp lực mới tạo ra động lực.",
  "Khóc cho bản thân nghe, cười cho người khác thấy, đó chính là trưởng thành.",
  "Nỗ lực là tên gọi khác của phép màu!",
  "Ước mơ không phụ thuộc vào tuổi tác, bởi vì trong mắt họ vẫn ngập tràn ánh sáng!",
  "Chỉ cần bạn còn giữ hy vọng thì nhất định theo đuổi được ước mơ.",
  "Những ngày tháng dường như tầm thường này, vào một ngày nào đó sẽ khiến bạn hiểu ra ý nghĩa của sự kiên trì.",
  "Hôm nay học một chút, ngày mai giỏi hơn một chút.",
  "Không ai có thể học thay bạn. Hãy bắt đầu ngay!",
  "Kiến thức hôm nay là thành công ngày mai.",
  "Sự chăm chỉ đánh bại tài năng nếu tài năng không chăm chỉ.",
  "Từng bước nhỏ sẽ tạo nên hành trình lớn.",
  "Kỷ luật là cầu nối giữa mục tiêu và thành tựu.",
  "Đừng đợi cảm hứng – hãy bắt đầu và cảm hứng sẽ đến.",
  "Nếu lúc nào bạn cũng sợ thất bại, thì thời gian trôi qua bạn vẫn là người thất bại, bạn chập nhận điều đó sao?",
  "Bạn hứa với mình rằng bạn sẽ không bao giờ bỏ cuộc nhé!",
  "Thiên tài là cái gì chứ? Nếu như không có tài năng thì bạn hãy dùng sự cần cù để chiến thắng cái gọi là 'Thiên tài'.",
  "Lẽ ra Napoleon nên nói là... từ 'Không thể' chỉ tồn tại trong từ điển của những 'kẻ ngốc' mà thôi.",
  "Đừng để cho sự tầm thường, dễ dãi ám ảnh mình. Chỉ có khát vọng và hoài bão lớn về sự sáng tạo thì mới đi được xa vfa bền vững.",
  "Học hỏi là chìa khóa mở ra cánh cổng thành cống.",
  "Mỗi ngày là một cơ hội để trở nên tốt hơn!",
  "Bạn không thể thay đổi quá khứ, nhưng bạn có thể thay đổi tương lai bằng cách học hỏi hôm nay.",
  "Cơ hội sẽ rộng mở khi bạn có một nền tảng tri thức tốt.",
  "Vũ trụ có bao la nhưng bạn là duy nhất!",
  "Giới hạn tầm nhìn nhưng không giới hạn con đường mà bạn đi.",
  "Không bao giờ là quá trễ để trở thành phiên bản tốt hơn của chính mình.",
  "Thất bại sẽ không bao giờ thắng được chúng ta nếu quyết tâm thành công của chúng ta đủ lớn.",
  "Xuất phát điểm không quyết định cho sự thành công của chúng ta.",
  "Những khó khăn và thử thách sẽ phải cuối đầu trước trái tim và lý trí quật cường của chúng ta.",
  "Kiêu ngạo là đặc quyền của kẻ mạnh!",
  "Tôi không tin vào may mắn! Vì tôi dùng nỗ lực để tạo nên may mắn cho chính mình. Còn bạn thì sao?",
  "Thắng không tự mãn, thua không suy sụp, không xem nhẹ rủi ro, không tùy tiện liều lĩnh!",
  "Không hời hợp, không trì hoãn, khó khăn đều nằm dưới chân, tương lai sẽ luôn tươi đẹp.",
  "Cuối đầu là sách vở, ngẩng đầu là tương lai!",
  "Hôm nay đọc sách, ngày mai đếm tiền!",
  "Đối thủ lớn nhất của con người chính là sự lười biếng của chính mình.",
  "Khi bạn cảm thấy con đường này đang khó đi, nhất định là bạn đang lên dốc.",
  "Bạn phải nỗ lực, cho chính bản thân những gì bạn muốn.",
  "Đi học không phải là lối thoát tốt nhất, nhưng là lối thoát quan trọng nhất.",
  "Sự tốt đẹp và thành công đều phải dựa vào sự phấn đấu của bạn mà có, không phải chờ đợi nó đến.",
  "Trong cái xã hội đen tối này, thứ sạch sẽ nhất chính là kiến thức.",
  "Quả cầu lông không thể rơi đúng chỗ, cho nên muốn đánh được cầu bạn phải di chuyển để bắt lấy nó.",
  "Thay vì chọn động lực, bạn hãy chọn kỷ luật.",
  "Dốt đến đâu học lâu cũng thấm, chỉ là bạn có cố gắng hay không thôi.",
  "Đừng học lúc tối muộn, hãy học lúc sáng sớm.",
  "Bỏ cuộc thì lấy gì đáp trả những lời miệt thị của họ.",
  "Nghị lực và nỗ lực sẽ chiến thắng tất cả.",
  "Chỉ việc học thật tốt còn thất bại thì nói gì đến sau này?",
  "Chậm chạp cũng được, không giỏi giang cũng được, điều quan trọng là bạn luôn nỗ lực hết mình.",
  "Hy vọng rằng thứ đánh thức bạn mỗi sáng không phải tiếng chuông báo thức mà là khát vọng lớn lao trong tim bạn.",
  "Dùng bút vẽ lên giấy. Dùng hiện tại viết tương lai.",
  "Bạn phải làm chủ kinh tế chính bản thân bạn thì hạnh phúc mới có thể đến với bạn.",
  "Bạn lười biếng cũng được, ăn chơi cũng được, nhưng bạn nên nhớ rằng không có gì là miễn phí. Điểm số cũng vậy!",
  "Khi bạn gặp khó khăn và cực khổ có nghĩa tương lai đang leo lên. Khi bạn an nhàn và lười biếng, nghĩa là tương lai của bạn đang trượt xuống.",
  "Mỗi khi bạn suy nghĩ đến việc học chính là thời khắc bạn trong tương lai đang mong cầu sự giúp đỡ của bạn hiện tại.",
  "Thất bại vài lần không có nghĩa bạn là người thất bại, mà các bạn là kẻ thất bại khi bạn chấp nhận buông xuối.",
  "Không có thời điểm nào là hoàn hảo để bắt đầu, thời điểm bắt đầu tốt đẹp nhất là ngày hôm nay và ngay bây giờ!",
  "Làm gì có ai yêu thích sự kỷ luật chứ? Nhưng người ta lại ghét nỗi đau của hối hận hơn.",
  "Ba mẹ chỉ cho bạn cái tên. Còn câu chuyện về cái tên đó là do bạn tự viết cho chính mình.",
  "Nếu bạn không đuổi kịp bình minh lúc 5 giờ sáng, vậy hãy thử ngắm hoàng hôn lúc 6 giờ chiều. Ý mình là bắt đầu lúc nào cũng không muộn, cuộc đời không phải là một cuộc đua, bạn không cần phải chạy cho bằng người khác, bạn chỉ cần đi theo nhịp của riêng mình.",
  "Đừng tự trách mình vì đã đến trễ, đừng buồn vì những điều chưa kịp , bắt đầu lúc nào cũng chưa bao giờ là quá muộn hết. Chỉ cần bạn vẫn còn tin, vẫn còn bước tiếp, thì mọi khoảnh khắc bạn chọn bắt đầu đều là khoảnh khắc đẹp nhất trong đời của mình.",
  "Nếu hôm nay mệt quá thì hãy cho phép bản thân mình thở một hơi thật là dài, nếu đã lỡ mất bình minh thì mình hẹn hoàng hôn nhé!",
  "Bầu trời vẫn rộng lắm, và cơ hội dành cho bạn chưa bao giờ khép lại, và mình tin trái tim kiên trì và dịu dàng như bạn rồi sẽ chạm được bầu trời thôi!",
  "Cuộc đời có kẽ hở, ánh sáng Mặt Trời mới có thể rọi vào. Không có màn đêm vĩnh hằng, chỉ có bình minh chưa đến.",
  "Cho nên chăm chỉ, lặp lại, luyện tập thường xuyên là cơ hội cho người bình thường đạt được thành công.",
  "Dù cho thế giới nghiệt ngã kia chê cười bạn, dù người đời có gièm pha thế nào đi nữa thì ta vẫn cứ bay lượn thôi. Bạn phải tin như thế!",
  "Nếu một mai không còn ánh sáng, bạn sẽ là ngọn đuốc của cuộc đời bạn.",
  "Hãy là ánh sáng của riêng bạn, không cần quá rực rỡ.",
  "Dũng cảm lên, dù sao thì cũng chỉ sống một lần. Làm gì có nhiều thời gian để nói 'Tôi không biết', 'Tôi sợ', 'Tôi không làm được'. Thay vì như thế thì không bằng cố gắng hết sức, đi làm những điều mình muốn làm, yêu những người mà mình muốn yêu.",
  "Bất cứ một cái khó khăn nào nó đều đi kèm với một hạt giống thành công. Khi mà bạn thất bại càng nhiều, cái sự thành công nó đến với bạn sau này càng lớn.",
  "Không ai quan tâm bạn bỏ ra bao nhiêu công sức, mệt mỏi hay không, ngã có đau không. Họ chỉ xem cuối cùng bạn đứng ở vị trí nào, sau đó ngưỡng mộ hoặc khinh thường.",
  "Tại sao bạn lại chọn an nhàn vào những năm tháng có thể cố gắng được.",
  "Đừng xấu hổ khi bạn không biết, chỉ xấu hổ khi bạn không học.",
  "Muốn bay cao? Đừng nỗ lực nửa vời, hãy nỗ lực hết sức!",
  "Không phụ ơn dạy dỗ, không phụ thịnh thế. Không hổ thẹn với bản thân, không hổ thẹn với thời đại. Chúc bạn thuận buồn xuôi gió, hẹn gặp nhau trên đỉnh vinh quang!",
  "Thiếu niên chính là thiếu niên, vừa khiêm tốn lại đôi chút ngạo nghễ, vừa kiêu hãnh lại đôi chút bình thản. Họ biết được những ưu, khuyết điểm của bản thân, không hề né tránh mà dũng cảm đối mặt. Bởi bì: Họ là thiếu niên, họ có thời gian để trải nghiệm!",
  "Bạn có thể là Mặt Trời, là dũng sĩ, là hiệp sĩ, có thể là một bài thơ bất định chiến lấy những thành trì của tương lai. Chúc bạn tương lai luôn rực rỡ, xán lạn, tươi sáng rạn ngời, bất khả chiến bại, không có gì là không làm được!",
  "Tôi kém hơn nhiều người, đương nhiên cũng có nhiều người kém hơn tôi. Gió lớn thổi qua cây ngô đồng luôn có người đánh giá độ ngắn dài. Mọi thứ bạn nhìn thấy ở tôi, tốt hay xấu tôi đều không phản bác. Tôi làm tốt việc của mình, bạn sống cuộc đời của bạn. Chúng ta tự có con đường của riêng mình.",
  "Là người trẻ sao lại đi mang chí an phận thủ thường, thật uổng công một đời đèn sách.",
  "Khi một người tiến bộ nhanh nhất là khi họ bắt buộc phải vượt qua nỗi sợ, sự dựa dẫm và thất vọng. Sau đó từng chút một hoàn thiện bộ giáp của mình, bắt đầu tỉnh ngộ, bắt đầu tự kiểm soát được cuộc sống, tự chủ cảm xúc, không còn nước mắt, cũng không còn bị kiểm soát dẫn dắt nữa.",
  "Tôi sẵn sàng thay đổi tất cả những gì mình có thể để trở thành phiên bản tốt hơn của chính mình. Bởi ai cũng hướng đến những gì tốt đẹp nhất với mình, và khi cơ hội đến chắc chắn tôi sẽ nắm lấy và sẵn sàng thay đổi.",
  "Bạn muốn biết bạn là ai? Đừng hỏi nữa. Hãy hành động! Hành động sẽ định nghĩa con người bạn.",
  "Mình leo lên đỉnh núi không phải để cả thế giới ngước lên chiêm ngưỡng mình, mình leo lên đỉnh núi để chính minh có thể chiêm ngưỡng cả thế giới.",
  "Mọi sự thành công đều xuất phát từ những nỗ lực không ngừng nghỉ, kiên trì không biết mệt mỏi.",
  "Thiên tài chỉ có 1% là bẩm sinh, 99% còn lại là mồ hôi và nước mắt.",
  "Mỗi con người ưu tú mà hôm nay bạn thấy, họ đều trải qua những quá trình khổ luyện. Và nhớ nhé, chưa ai chết đuối trong mồ hôi của chính mình cả.",
  "Những kẻ mạnh không phải lúc nào cũng chiến thắng, mà kẻ chiến thắng mới là kẻ mạnh.",
  "Nếu bạn cảm thấy mông lung và thiếu động lực để cố gắng thì hãy nhớ rằng: món đồ bạn thích rất đắt đỏ, người bạn thích rất ưu tú. Và thế giới rộng lớn, đẹp đẽ đến như vậy, bố mẹ bạn xứng đáng được nhìn ngắm một lần.",
  "Khi còn trẻ thì người ta sẽ nhìn vào ba mẹ của các bạn để người ta đối xử với các bạn. Khi các bạn lớn lên rồi, người ta sẽ nhìn vào các bạn để đối xử với bố mẹ các bạn.",
  "Phải nhớ rằng: 'Tốc độ thành công của bạn luôn luôn phải nhanh hơn tốc độ già đi của bố mẹ bạn!', bạn phải luôn nhớ điều đó, phải tâm tâm niệm niêm điều đó.",
  "Hãy học khi người khác ngủ, lao động khi người khác lười nhác, chuẩn bị khi người khác chơi bời. Rồi bạn sẽ đạt được ước mơ khi người khác chỉ ao ước. Hãy nhớ!",
  "Khi bạn đang thoải mái nằm, đừng quên người khác đang cố gắng chạy!",
  "Đừng quan tâm người khác nói gì về bạn, bởi vì những người giỏi hơn bạn. Căn bản không thèm nhắc đến bạn.",
  "Đến bây giờ, trên vai bạn không chỉ còn đơn thuần là chiếc cặp nữa. Bây giờ, ở đó là sự kỳ vọng của tất cả những người yêu thương mình, niềm tự hào của gia đình. Ván cược này, mình nhất định sẽ thắng.",
  "Muốn ngồi ở vị trí không ai ngồi được thì phải chịu đựng cảm giác không ai chịu được.",
  "Ngạo nghễ là khi: 'Bản thân không cần giới thiệu mà mọi người vẫn biết bạn là ai!'.",
  "Cái được gọi là 'Một đêm thành danh' thực chất là 'Nghìn đêm nỗ lực'.",
  "Tri thức là hành trang, kỹ năng là vũ khí. Càng chuẩn bị sớm, càng tiến xa hơn.",
  "Học mỗi ngày để không lùi bước, làm mỗi giờ để không bị bỏ lại phía sau.",
  "Muốn học giỏi thì phải có sự kỷ luật, chứ chỉ có động lực thôi thì không bao giờ đủ.",
  "Làm gì có chuyện tôi tự dưng lao đầu vào học như vậy, tất cả là vì tôi nếm quá đủ thất vọng rồi.",
  "Kỷ luật sẽ đưa bạn đến nơi mà động lực không làm được.",
  "Làm để giỏi! Đừng đợi giỏi mới làm.",
  "Người chiến thắng là người biết ước mơ và không bao giờ bỏ cuộc.",
  "Nếu muốn bay cao cùng đại bàng thì đừng để tâm đến quạ đen.",
  "Vì biết bản thân mình không phải người giỏi nhất nên bắt buộc phải là người chăm chỉ nhất.",
  "Đừng học vì điểm số, đừng học chỉ vì muốn hơn thua với ai cả. Hãy học để sau này không phải cuối đầu trước bất kỳ ai, hãy học vì bạn muốn tìm hiểu và khám phá những thứ bản thân mình chưa biết.",
  "Đời này, bạn không cần chạy đua để chứng minh giá trị của mình với ai cả, hoa thơm không năn nỉ ông bướm tới, trời xanh không cần ai công nhận nó cao.",
  "Không cần ai công nhận bạn đâu, chỉ cần bạn tự nhận ra giá trị của bản thân là được rồi.",
  "Cố học đi em, cha mẹ cần một người thành công chứ không phải một người lười nhác.",
  "Nên nhớ, muốn học giỏi thì phải có sự kỷ luật, chứ chỉ có động lực thôi thì không bao giờ đủ. Động lực nó chỉ giúp chúng ta một phần nhỏ trong con đường thành công thôi.",
  "Người chăm học có một kiểu đẹp rất riêng: Đẹp của bản lĩnh, đẹp của kiên trì và đẹp của tương lai rực rỡ.",
  "Tuổi trẻ không sợ gì, chỉ sợ không đủ rực rỡ. Mong bạn trở thành dáng vẻ mình yêu thích, tự do tự tại, rựa rỡ ánh hào quang.",
  "Đừng để những thành tích người khác khoe khiến bạn cảm thấy mình kém ỏi. Ai cũng chỉ muốn cho thế giới thấy mặt rực rỡ nhất của mình. Bạn chỉ cần kiên định với con đường mình đã chọn và vững vàng tiến bước đến đích cuối cùng.",
  "Hào quang không đến từ may mắn. Nó đến từ những đêm cày nát tập, mà không ai thấy.",
  "Học đi, rồi bạn sẽ thấy, thay vì lo lắng mình có đủ tốt không. Bạn sẽ bắt đầu tự tin rằng: 'Mình xứng đáng hơn cả thế!'.",
  "Tôi không sinh ra để thua. Tôi sinh ra để chiến thắng.",
  "Giống như một quặng sắt, nó không thể biến thành vàng. Nhưng nếu được rèn giũa đúng cách, nó sẽ trở thành một lưỡi dao sắt bén, cắt gọt những thỏi vàng.",
  "Điều khiến ta gục ngã không phải là những lời chê bai, mà là vì ta cho phép điều đó định nghĩa giá trị của mình. Đừng thu mình để vừa vặn với cái nhìn của người khác, bởi vì không cần một chiếc khung, ta vẫn có thể tự vẽ nên bức trang của chính mình.",
  "Sức mạnh không đến từ xuất thân mà đến từ ý chí, nghị lực và trái tim của mỗi con người. Hãy luôn tin vào giá trị của bản thân. Bạn là duy nhất và đó là sức mạnh!",
  "Không cần phải hoàn hảo để trở nên tỏa sáng, chỉ cần là chính mình sẽ tỏa sáng!",
  "Bãn lĩnh không phải là không gục ngã, mà là dám mạnh mẽ đứng dậy, để chạm tay vào ước mơ thêm một lần nữa!",
  "Không có đơn vị nào đo lường cho sự thành công hay thất bại!",
  "Tương lai không được chờ đợi mà nó được tạo ra!",
  "Kỳ tích chỉ nở hoa trên mảnh đất của lòng dũng cảm!",
  "Chiều cao không tính bằng số đo, mà nó được tính từ đỉnh đầu cho tới bầu trời của những ước mơ.",
  "Xin nhắc lại một lần nữa: 'Nếu bạn không bước, người khác sẽ đá bạn ra khỏi đường đua.'",
  "Nếu kỳ tích không chiếu cố bạn, hãy biến bản thân trở thành kỳ tích!",
]

const randomQuote = ref ('')

onMounted(() => {
  const index = Math.floor(Math.random() * quotes.length)
  randomQuote.value = quotes[index]
})

</script>

<style scoped>
.landing-page {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background-color: #000;
}

.content {
  position: relative;
  z-index: 1;  /* Nằm trên cùng */
  color: white;
  text-align: center;
  padding-top: 5vh;
}

.button-group {
  font-weight: bold;
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  text-decoration: none;
}

.btn {
  width: 200px;
  padding: 0.8em 2em;
  font-size: 1.1rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.3s;
}

.login-btn {
  background-color: #3498db;
  color: white;
}

.login-btn:hover {
  background-color: #2980b9;
}

.register-btn {
  background-color: #2ecc71;
  color: white;
}

.register-btn:hover {
  background-color: #27ae60;
}

.quote-box {
  margin-top: 2rem;
  text-align: center;
}

.motivational-quote {
  font-size: 1.5rem;
  font-style: italic;
  color: #333;
}

</style>