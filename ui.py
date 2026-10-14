

import pygame
import sys
import threading

from cam import Camera

from ocr import OCR


# from runsummarizer import Summarizer
from runcloudsummarizer import CloudSummarizer

pygame.init()

WIDTH, HEIGHT = 800, 480
FPS = 30

blk = (0, 0, 0)
wht = (255, 255, 255)
FG = blk
BUTTON = (200, 200, 200)
HINT = (0, 180, 180)


class App:
    def __init__(self):

        self.camera = Camera(width=640, height=480) #preview res

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("scan device")
        self.clock = pygame.time.Clock()

        self.f_title  = pygame.font.SysFont("dejavusans,arial,helvetica", 36, bold=True)
        self.f_body   = pygame.font.SysFont("dejavusans,arial,helvetica", 22)
        self.f_button = pygame.font.SysFont("dejavusans,arial,helvetica", 26, bold=True)

        self.state = "idle"
        self.resultText = ""
        self.rescanButton = pygame.Rect(0, 0, 0, 0)

        # background job state
        self._job_result = None
        self._job_done = False

        # load model in background so UI comes up immediately
        self.summarizer = None
        threading.Thread(target=self._load_model, daemon=True).start()

        self.ocr = OCR()


    
    def _load_model(self):
        print("loading model...")
        self.summarizer = CloudSummarizer()
        print("model ready")






    def _summarize_worker(self):
        try:
            # get frame
            frame = self.camera.get_frame()

            # extract text
            text = self.ocr.extract(frame)
            print(f"OCR text ({len(text)} chars): {text[:100]}...")

            if len(text) < 20:
                self._job_result = "didnt detect text"
            else:
                self._job_result = self.summarizer.summarize(text)

        except Exception as e:
            print(f"Error: {e}")
            self._job_result = "something went wrong"

        self._job_done = True

    def checkJob(self):
        if self.state == "processing" and self._job_done:
            self.resultText = self._job_result or "no summary produced"
            self._job_done = False
            self._job_result = None
            self.state = "result"

            print("START")
            print(self.resultText)
            print("END")


            #self.resultText = self.trimDown(self.resultText)






    def wrapText(self, text, charsPerLine=35):
        words = text.split()
        lines, current = [], ""
        for word in words:
            if len(current) + len(word) + 1 <= charsPerLine:
                current = (current + " " + word).strip()
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    """ 
    def trimDown(self, text, maxChars=500):

        count = 0
        for i, ch in enumerate(text):
            if ch in ".!?":
                count += 1
                if count == 3: #                                                            <- change hard sentence count here
                    text = text[:i + 1].strip()
                    break
        else:
            text = text.strip()

        if len(text) > maxChars:
            text = text[:maxChars].rstrip() + "..."
        return text
    """





    def run(self):
        while True:
            self.handleEvents()
            self.checkJob()
            self.draw()
            self.clock.tick(FPS)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handleTap(event.pos)

    def handleTap(self, pos):
        if self.state == "idle":
            if self.summarizer is None or self.camera is None:
                self.resultText = "still loading, please wait"
                self.state = "result"
                return

            #fakeOcrText = ("The design of the Eiffel Tower is attributed to Maurice Koechlin and Émile Nouguier, two senior engineers working for the Compagnie des Établissements Eiffel. It was envisaged after discussion about a suitable centrepiece for the proposed 1889 Exposition Universelle, a world's fair to celebrate the centennial of the French Revolution. In May 1884, working at home, Koechlin made a sketch of their idea, described by him as a great pylon, consisting of four lattice girders standing apart at the base and coming together at the top, joined together by metal trusses at regular intervals. Eiffel initially showed little enthusiasm, but he did approve further study, and the two engineers then asked Stephen Sauvestre, the head of the company's architectural department, to contribute to the design. Sauvestre added decorative arches to the base of the tower, a glass pavilion to the first level, and other embellishments.")
            #fakeOcrText = ("MENAGERIE What compels us to collect? The act of collecting is something many of us share. In this gallery we've assembled a menagerie of small animal themed objects for you to explore. As you look at our cabinet of curiosities, you might think about ways that artists have brought animals together in individual works of art. You might be surprised at what you find.")
            #fakeOcrText = ("Idelle Weber is associated with the Photorealists. In the early 1970s she became interested in studying and depicting the piles of cast-off objects lying along city gutters and sidewalks. The meticulous detail and vivid clarity of color, texture and light in Weber's Heineken remind us that she used photographs as a preliminary step to the finished painting. Weber searched city streets for accidental arrangements of litter that she found evocative in terms of color, shape and texture. She photographed the arrangement using 35mm color slide film, and used these images as memory aids in creating the final painting.")
            #fakeOcrText = ("Baron François-Pascal-Simon Gérard (French, 1770-1837) Madame Charles-Maurice de Talleyrand-Périgord, Princesse de Bénévent (née Catherine Noele Worlée, later Madame George Francis Grand, 1762-1835), ca. 1808 This painting portrays one of the celebrated beauties of her time, Catherine Worlée (1762-1835). By the age of fifteen she had seduced her future husband, the Englishman George Francis Grand, an employee of the Indian civil services (as Madame Grand she was portrayed by Vigée Lebrun in an oval portrait displayed in this gallery). This was the first of a series of liaisons that culminated in her becoming the mistress and then the wife of Talleyrand, whose portrait by Prud'hon hangs nearby. Talleyrand tired of his pretty but frivolous wife, whom he had sent away in 1817. After residing in London and Brussels, she returned to Paris, where, separated from her husband, she lived a quiet and devout life.")

            self.state = "processing"
            self._job_done = False
            self._job_result = None
            threading.Thread(
                target=self._summarize_worker,
                daemon=True
            ).start()

        elif self.state == "result":
            if self.rescanButton.collidepoint(pos):
                self.state = "idle"


    def draw(self):
        self.screen.fill(wht)
        if self.state == "idle":
            self.drawIdle()
        elif self.state == "processing":
            self.drawProcessing()
        else:
            self.drawResult()
        pygame.display.flip()

    def drawIdle(self):
        # cam preview
        frame = self.camera.get_frame()
        surf = pygame.image.frombuffer(
            frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB"
        )
        surf = pygame.transform.smoothscale(surf, (WIDTH, HEIGHT))
        self.screen.blit(surf, (0, 0))

        # transparent text
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))   # last value = alpha (0-255)
        self.screen.blit(overlay, (0, 0))

        title = self.f_title.render("Tap anywhere to scan", True, wht)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    def drawProcessing(self):
        title = self.f_title.render("Processing...", True, blk)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))

        hint = self.f_body.render("Summarizing the label", True, HINT)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

    def drawResult(self):
        header = self.f_title.render("Summary", True, FG)
        self.screen.blit(header, (40, 30))

        margin = 40
        y = 110
        line_height = self.f_body.get_linesize() + 6

        for line in self.wrapText(self.resultText, charsPerLine=60):
            if y > HEIGHT - 110:
                break
            surf = self.f_body.render(line, True, FG)
            self.screen.blit(surf, (margin, y))
            y += line_height

        btn_w, btn_h = 220, 60
        btn_x = WIDTH - btn_w - 40
        btn_y = HEIGHT - btn_h - 30
        self.rescanButton = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.screen, BUTTON, self.rescanButton, border_radius=12)
        label = self.f_button.render("Scan again", True, FG)
        self.screen.blit(label, (
            btn_x + btn_w // 2 - label.get_width() // 2,
            btn_y + btn_h // 2 - label.get_height() // 2
        ))


    def quit(self):
        pygame.quit()
        self.camera.release()
        sys.exit()
        


if __name__ == "__main__":
    App().run()
