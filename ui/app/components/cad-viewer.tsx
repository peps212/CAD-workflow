"use client"

import { useEffect, useRef, useState } from 'react'
import "../../dist/three-cad-viewer/three-cad-viewer.css"
import { Viewer } from "../../dist/three-cad-viewer/three-cad-viewer.esm.js"

export interface CadViewerProps {
    cadShapes: any
}


export default function CadViewer({ cadShapes }: CadViewerProps) {
    const ref = useRef(null)
    const [viewerDimensions, setViewerDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        
        setViewerDimensions({
            width: window.innerWidth,
            height: window.innerHeight,
        });
    }, []);

    const viewerOptions = {
        theme: "light",
        ortho: true,
        control: "trackball", 
        normalLen: 0,
        cadWidth: viewerDimensions.width,
        height: viewerDimensions.height * 0.85,     
        ticks: 10,
        ambientIntensity: 0.9,
        directIntensity: 0.12,
        transparent: false,
        blackEdges: false,
        axes: true,
        grid: [false, false, false],
        timeit: false,
        rotateSpeed: 1,
        tools: false,
        glass: false
    }

    const renderOptions = {
        ambientIntensity: 1.0,
        directIntensity: 1.1,
        metalness: 0.30,
        roughness: 0.65,
        edgeColor: 0x707070,
        defaultOpacity: 0.5,
        normalLen: 0,
        up: "Z"
    }


    useEffect(() => {
        const container = ref.current //document.getElementById("cad_view")

        

        // var shapesStates = viewer.renderTessellatedShapes(shapes, states, options)
        if (cadShapes && cadShapes.length > 0) {
            const viewer = new Viewer(container, viewerOptions)

            render("input", ...cadShapes)
            function render(name: string, shapes, states) {
                viewer?.clear()
                const [unselected, selected] = viewer.renderTessellatedShapes(shapes, states, renderOptions)
                console.log(unselected)
                console.log(selected)

                viewer.render(
                    unselected,
                    selected,
                    states,
                    renderOptions,
                )
            }
        }


    }, [cadShapes])

    return (
        <div ref={ref}></div>
    )
}