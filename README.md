Link project on Github: https://github.com/trihieuvo/8_puzzle_solver.git

# 🧩 Giải 8-Puzzle với Pygame và Các Thuật Toán Tìm Kiếm

Một ứng dụng desktop được xây dựng bằng Pygame để mô phỏng và giải bài toán 8-puzzle sử dụng nhiều thuật toán tìm kiếm khác nhau, bao gồm cả các thuật toán cơ bản và nâng cao, cũng như các biến thể ứng dụng khái niệm And-Or Tree cho phép "di chuyển kép".

## ✨ Tính năng nổi bật

*   **Giao diện đồ họa trực quan:** Được xây dựng trên Pygame, dễ dàng tương tác và theo dõi quá trình giải đố.
*   **Đa dạng thuật toán:** Bao gồm các nhóm thuật toán tìm kiếm không thông tin, có thông tin, tìm kiếm cục bộ, giải quyết CSP, tìm kiếm trong môi trường phức tạp và học tăng cường.
*   **Hỗ trợ "Di Chuyển Kép" (Ứng dụng And-Or Tree):** Nhiều thuật toán có phiên bản "ANDOR" hoặc "Double Moves", mô phỏng việc ô trống có thể thực hiện một hoặc hai bước di chuyển hợp lệ trong một lượt, coi như một ứng dụng của cây And-Or trong không gian trạng thái.
*   **Hoạt ảnh Điền Số (Fill Animation):** Sử dụng thuật toán **Backtracking** để mô phỏng trực quan quá trình điền tuần tự các số (từ 1 đến 9) vào một lưới 8-puzzle trống để đạt được một trạng thái đích cho trước. Hiển thị cả các bước "thử" và "lui" của thuật toán.
*   **Tìm kiếm Mù trong Môi trường Phức Tạp (Blind Belief Search):** Tính năng "Blind Search" mô phỏng việc tìm kiếm giải pháp trong một môi trường mà agent không hoàn toàn quan sát được trạng thái thực tế (partially observable). Agent duy trì một "belief state" (tập hợp các trạng thái có thể) và tìm một chuỗi hành động chung để đưa *tất cả* các trạng thái trong belief state hiện tại về một trong các trạng thái đích đã định nghĩa. Đây là một ví dụ về tìm kiếm trong không gian belief state.
*   **Tùy chỉnh trạng thái:** Cho phép người dùng chỉnh sửa trạng thái ban đầu của puzzle.
*   **Hoạt ảnh các bước giải:** Trực quan hóa từng bước di chuyển của ô trống.
*   **Điều chỉnh tốc độ hoạt ảnh.**
*   **So sánh thuật toán:** Dễ dàng chọn và chạy các thuật toán khác nhau để quan sát hiệu quả.

## 📸 Demo Giao Diện & Thuật Toán

**1. Giao diện Chính (Menu lựa chọn thuật toán):**
![Demo Menu Chính](assets/demo_main_menu.gif)
*Mô tả: Người dùng có thể chọn thuật toán từ danh sách bên trái, chỉnh sửa trạng thái ban đầu, hoặc truy cập các tính năng đặc biệt.*

**2. Giao diện Giải:**
![Demo Giải 8_puzzle](assets/demo_solver_interface.gif)
*Mô tả: Hiển thị puzzle đang được giải, thông tin về thuật toán, các bước giải và các nút điều khiển hoạt ảnh, thanh chỉnh tốc độ,...*

**3. Tính năng "Di Chuyển Kép" (Ứng dụng And-Or Tree):**
![Demo Di Chuyển Kép](assets/demo_double_moves.gif)
*Mô tả: Minh họa thuật toán (ví dụ Beam Search) tìm đường đi có thể bao gồm các bước di chuyển kép của ô trống, thường cho lộ trình ngắn hơn về số lượt (mặc dù lượt đi kép có thể tốn chi phí cao hơn).*

**4. Tìm kiếm Mù (Blind Belief Search):**
![Demo Tìm Kiếm Mù](assets/demo_blind_search.gif)
*Mô tả: Giao diện hiển thị 2 puzzle (đại diện cho các trạng thái trong belief state) được giải đồng thời bằng một chuỗi hành động chung. Thông tin về quá trình tìm kiếm belief state cũng được hiển thị.*

**5. Hoạt ảnh Điền Số (Fill Animation):**
![Demo Hoạt Ảnh Điền Số](assets/demo_fill_animation.gif)
*Mô tả: Trực quan hóa thuật toán backtracking điền các số vào lưới để đạt được trạng thái đích.*

**6. Giao diện Chỉnh Sửa Trạng Thái:**
![Demo Chỉnh Sửa Trạng Thái](assets/demo_edit_state.gif)
*Mô tả: Người dùng có thể dễ dàng thay đổi các ô số để tạo trạng thái ban đầu mong muốn.*

## 📂 Cấu trúc Thư mục Dự án

* ├── algorithms/ # Chứa các file triển khai thuật toán  
* ├── assets/ # Chứa ảnh và GIF demo  
* ├── blind.py # Logic cho tính năng tìm kiếm mù (Blind Belief Search) cho nhiều trạng thái  
* ├── fill.py # Logic cho hoạt ảnh điền số vào lưới bằng Backtracking
* ├── main.py # File chạy chính của ứng dụng
* ├── README.md # File mô tả dự án này
* └── .gitignore # Các file/thư mục Git bỏ qua

## 💡 Các Thuật Toán Được Triển Khai

Dự án này minh họa một loạt các thuật toán giải quyết vấn đề, được phân loại như sau. Nhiều thuật toán trong số này có cả phiên bản chuẩn (di chuyển đơn) và phiên bản hỗ trợ "di chuyển kép" (được đánh dấu là `_ANDOR` hoặc `(Double Moves)` trong giao diện), thể hiện một ứng dụng của khái niệm cây And-Or trong việc mở rộng không gian trạng thái.

**1. Tìm kiếm Không Thông Tin (Uninformed Search / Blind Search)**
* Mục tiêu là tìm đường đi mà không sử dụng thông tin đặc thù về bài toán (heuristic). 
    *   **Breadth-First Search (BFS):** Duyệt theo chiều rộng, đảm bảo tìm ra đường đi ngắn nhất về số bước.
        *   `BFS` (Di chuyển đơn)
        *   `BFS (Double Moves)` / `bfs_ANDOR`
    *   **Depth-First Search (DFS):** Duyệt theo chiều sâu, có thể tìm ra giải pháp nhanh nhưng không đảm bảo tối ưu.
        *   `DFS` (Di chuyển đơn)
        *   `DFS (Double Moves)` / `dfs_ANDOR`
    *   **Iterative Deepening DFS (IDDFS):** Kết hợp ưu điểm của BFS (tối ưu) và DFS (không gian bộ nhớ).
        *   `IDDFS` (Di chuyển đơn)
        *   `IDDFS (Double Moves)` / `iddfs_ANDOR`
    *   **Uniform-Cost Search (UCS):** Tìm đường đi với chi phí thấp nhất (khi các hành động có chi phí khác nhau).
        *   `UCS` (Di chuyển đơn, chi phí mỗi bước là 1)
        *   `UCS (Double Moves)` / `ucs_ANDOR` (Di chuyển đơn chi phí 1, di chuyển kép chi phí 2)

**2. Tìm kiếm Có Thông Tin (Informed Search / Heuristic Search)**
* Sử dụng hàm đánh giá (heuristic) để hướng dẫn quá trình tìm kiếm, thường hiệu quả hơn Uninformed Search.
    *   **Greedy Best-First Search:** Luôn ưu tiên mở rộng nút có vẻ "gần" đích nhất theo heuristic.
        *   `Greedy Search` (Di chuyển đơn)
        *   `Greedy Search (Double Moves)` / `greedy_ANDOR`
    *   **A* Search:** Kết hợp chi phí thực tế đã đi (g) và chi phí ước lượng còn lại (h) để tìm đường đi tối ưu về tổng chi phí.
        *   `A* Search` (Di chuyển đơn, sử dụng heuristic Manhattan)
        *   `A* Search (Double Moves)` / `a_star_ANDOR` (Sử dụng heuristic Manhattan, di chuyển kép có chi phí cao hơn)
    *   **Iterative Deepening A* (IDA*):** Tương tự IDDFS nhưng sử dụng hàm f(n) = g(n) + h(n) làm giới hạn.
        *   `IDA* Search` (Di chuyển đơn)
        *   `IDA* (Double Moves)` / `ida_star_ANDOR`

**3. Tìm kiếm Cục Bộ (Local Search)**
* Các thuật toán này duyệt qua không gian trạng thái bằng cách di chuyển từ trạng thái hiện tại sang một trạng thái lân cận, thường không lưu trữ đường đi chi tiết mà chỉ tập trung vào trạng thái hiện tại và trạng thái tốt nhất đã tìm thấy.
    *   **Hill Climbing:**
        *   `Simple Hill Climbing`: Di chuyển đến lân cận tốt hơn đầu tiên tìm thấy (trong project này, logic có thể chọn ngẫu nhiên trong các bước cải thiện).
            *   `Hill Climbing` (Di chuyển đơn)
            *   `Hill Climbing (Double Moves)` / `hill_climbing_ANDOR`
        *   `Steepest Ascent Hill Climbing`: Di chuyển đến lân cận *tốt nhất* trong số tất cả các lân cận.
            *   `Steepest Ascent Hill Climbing` (Di chuyển đơn)
            *   `Steepest Ascent Hill Climbing (Double Moves)` / `steepest_hill_ANDOR`
        *   `Stochastic Hill Climbing`: Chọn một lân cận tốt hơn một cách ngẫu nhiên từ các lân cận cải thiện.
            *   `Stochastic Hill Climbing` (Di chuyển đơn)
            *   `Stochastic Hill Climbing (Double Moves)` / `stochastic_hc_ANDOR` (*Chính xác là stochastic_hill_ANDOR.py*)
    *   **Local Beam Search:** Giữ lại một số lượng (`beam_width`) các trạng thái tốt nhất ở mỗi bước để khám phá song song.
        *   `Beam Search` (Di chuyển đơn)
        *   `Beam Search (Double Moves)` / `beam_search_ANDOR`
    *   **Simulated Annealing:** Cho phép di chuyển đến trạng thái xấu hơn với một xác suất nhất định (giảm dần theo "nhiệt độ") để thoát khỏi cực trị địa phương.
        *   `Simulated Annealing` (Di chuyển đơn)
        *   `Simulated Annealing (Double Moves)` / `simulated_annealing_ANDOR`

**4. Giải Quyết Vấn Đề Thỏa Mãn Ràng Buộc (Constraint Satisfaction Problems - CSPs)**
* Việc điền số vào lưới 8-puzzle được xem như một dạng CSP.
    *   **Backtracking Search:** Sử dụng trong tính năng "Hoạt ảnh Điền Số" (`fill.py`) để tìm một cách điền các số từ 1-9 vào lưới sao cho thỏa mãn trạng thái đích. Thuật toán thử các giá trị và quay lui nếu gặp ngõ cụt.

**5. Tìm kiếm trong Môi trường Phức Tạp (Searching in Complex Environments)**
    *   **Searching with No Observation (Blind Belief Search):** 
    * Triển khai trong `blind.py`. Agent không biết chắc chắn trạng thái hiện tại của mình mà duy trì một "belief state" (tập hợp các trạng thái có thể). Mục tiêu là tìm một chuỗi hành động chung để đưa tất cả các trạng thái trong belief state về một trong các trạng thái đích. Đây là một ví dụ về tìm kiếm trong không gian belief state, sử dụng BFS trên các belief state.

**6. Học Tăng Cường (Reinforcement Learning)**
* Agent học cách hành động tối ưu thông qua tương tác với môi trường và nhận phản hồi (reward/penalty).*
    *   **Q-Learning:** Triển khai trong `q_learning.py`. Agent xây dựng một bảng Q-table để ước lượng giá trị của việc thực hiện một hành động tại một trạng thái cụ thể. Cần quá trình "huấn luyện" để bảng Q-table hội tụ.
        

---
**Giải thích về "Di Chuyển Kép" / Ứng dụng And-Or Tree:**
Các thuật toán có hậu tố `_ANDOR` hoặc được mô tả là `(Double Moves)` trong giao diện không chỉ xem xét việc di chuyển ô trống một bước (`OR-node` truyền thống) mà còn xem xét khả năng di chuyển ô trống hai bước liên tiếp như một "hành động" đơn lẻ phức tạp hơn.
Điều này có thể được coi là một ứng dụng của khái niệm cây And-Or (And-Or graph search) trong không gian trạng thái, nơi một "hành động" (AND-node) có thể bao gồm một chuỗi các hành động con (OR-nodes cho mỗi bước di chuyển cơ bản).
Mục tiêu là tìm ra một "chiến lược" di chuyển (có thể bao gồm cả bước đơn và bước kép) để đến đích. Trong các thuật toán như UCS và A*, các "hành động kép" này thường được gán chi phí cao hơn (ví dụ: chi phí 2) so với hành động đơn (chi phí 1). Điều này cho phép các thuật toán đánh giá và lựa chọn giữa việc thực hiện một bước dài hơn (tiềm năng giảm số lượt) với chi phí cao hơn, hoặc nhiều bước ngắn hơn với chi phí thấp hơn trên mỗi bước.

---

## 🛠️ Cài đặt và Chạy Dự án

**Yêu cầu:**
*   Python 3.7+
*   Pygame

**Các bước cài đặt:**

1.  Clone repository này:
    ```bash
    git clone https://github.com/trihieuvo/8_puzzle_solver.git
    cd 8_puzzle_solver
    ```

2.  (Khuyến nghị) Tạo và kích hoạt môi trường ảo:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  Cài đặt Pygame:
    ```bash
    pip install pygame
    ```

4.  Chạy ứng dụng:
    ```bash
    python main.py
    ```

## 🎮 Cách sử dụng

1.  Chạy `main.py`.
2.  Từ menu chính, chọn một thuật toán từ danh sách bên trái.
3.  Nhấn nút "Bắt đầu" để xem thuật toán giải puzzle với trạng thái ban đầu mặc định.
4.  Sử dụng các nút "Auto", "Tiếp theo", "Làm lại" để điều khiển hoạt ảnh khi xem giải đố.
5.  Thanh trượt tốc độ cho phép điều chỉnh tốc độ di chuyển của các ô.
6.  Nút "Chỉnh sửa trạng thái" cho phép bạn tùy chỉnh trạng thái ban đầu của puzzle.
7.  Nút "Tìm kiếm mù" để chạy demo Blind Belief Search.
8.  Nút "Hoạt ảnh điền số" để xem demo Backtracking điền số.

## 👨‍💻 Tác giả

*   **Võ Trí Hiệu**
*   Email: <hieu981.vn@gmail.com>
*   GitHub: https://github.com/trihieuvo
