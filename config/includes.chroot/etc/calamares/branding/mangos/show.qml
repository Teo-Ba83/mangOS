/* MangOS installation slideshow (Calamares slideshow API 2, Qt 6). */
import QtQuick
import calamares.slideshow 1.0

Presentation {
    id: presentation
    property bool it: Qt.locale().name.substring(0, 2) === "it"

    function onActivate() { timer.running = true }
    function onLeave()    { timer.running = false }

    Timer {
        id: timer
        interval: 9000
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    component MSlide: Slide {
        property alias title: t.text
        property alias body: b.text
        property alias picture: img.source
        Rectangle { anchors.fill: parent; color: "#FFFFFF" }
        Image {
            id: img
            width: 200; height: 200
            fillMode: Image.PreserveAspectFit
            smooth: true
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top; anchors.topMargin: 36
        }
        Text {
            id: t
            anchors.top: img.bottom; anchors.topMargin: 22
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: "Inter"; font.pixelSize: 26; font.weight: Font.DemiBold
            color: "#1D1D1F"
        }
        Text {
            id: b
            anchors.top: t.bottom; anchors.topMargin: 12
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.7
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.family: "Inter"; font.pixelSize: 15
            color: "#6E6E73"
            lineHeight: 1.25
        }
    }

    MSlide {
        picture: "welcome.png"
        title: presentation.it ? "Benvenuto in MangOS" : "Welcome to MangOS"
        body: presentation.it
              ? "Un sistema leggero e pulito, pensato per dare nuova vita al tuo Mac."
              : "A light, clean system made to give your Mac a new life."
    }
    MSlide {
        picture: "slide-artcraft.png"
        title: presentation.it ? "Le app ArtCraft, già pronte" : "ArtCraft apps, ready to go"
        body: presentation.it
              ? "WordCraft per scrivere, PdfCraft per i PDF e PhotoCraft per le foto. Altre app sono a un clic nel launcher ArtCraft."
              : "WordCraft for writing, PdfCraft for PDFs and PhotoCraft for photos. More apps are one click away in the ArtCraft launcher."
    }
    MSlide {
        picture: "slide-appearance.png"
        title: presentation.it ? "Chiaro o scuro, scegli tu" : "Light or dark, your choice"
        body: presentation.it
              ? "Al primo avvio scegli l'aspetto che preferisci. Puoi cambiarlo quando vuoi dalle Impostazioni."
              : "Pick the look you like on first start. You can change it any time in Settings."
    }
    MSlide {
        picture: "slide-secure.png"
        title: presentation.it ? "Sicuro e aggiornato" : "Safe and up to date"
        body: presentation.it
              ? "Basato su Debian stabile, con aggiornamenti di sicurezza automatici."
              : "Built on Debian stable, with automatic security updates."
    }
}
